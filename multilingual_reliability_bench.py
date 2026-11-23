from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from collections import defaultdict
from typing import Callable, Sequence


ABSTENTION_MARKERS = (
    "i cannot answer",
    "i can't answer",
    "cannot determine",
    "can't determine",
    "insufficient information",
    "not enough information",
    "i don't know",
    "i do not know",
    "unable to verify",
    "cannot verify",
    "can't verify",
    "not supported",
)


@dataclass(frozen=True)
class PromptCase:
    language: str
    question_id: str
    prompt: str
    expected: str
    supported: bool = True
    expected_refusal: bool = False

    def __post_init__(self):
        for field_name in ("language", "question_id", "prompt"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")
        if not isinstance(self.expected, str):
            raise ValueError("expected must be a string")
        if type(self.supported) is not bool or type(self.expected_refusal) is not bool:
            raise ValueError("supported and expected_refusal must be booleans")
        if self.supported and not self.expected_refusal and not self.expected.strip():
            raise ValueError("answerable supported cases require a non-empty expected answer")


@dataclass(frozen=True)
class EvalResult:
    language: str
    question_id: str
    supported: bool
    expected_refusal: bool
    correct: bool
    abstained: bool
    over_answered_unsupported: bool
    unnecessary_abstention: bool
    response: str


LANGUAGE_ABSTENTION_MARKERS = {
    "bn": (
        "যথেষ্ট তথ্য নেই",
        "আমার কাছে যথেষ্ট তথ্য নেই",
        "আমি জানি না",
        "নির্ধারণ করতে পারি না",
        "যাচাই করতে পারি না",
        "উত্তর দিতে পারি না",
    ),
    "hi": (
        "पर्याप्त जानकारी नहीं",
        "मेरे पास पर्याप्त जानकारी नहीं",
        "मुझे नहीं पता",
        "निर्धारित नहीं कर सकता",
        "निर्धारित नहीं कर सकती",
        "सत्यापित नहीं कर सकता",
        "सत्यापित नहीं कर सकती",
        "उत्तर नहीं दे सकता",
        "उत्तर नहीं दे सकती",
    ),
    "ur": (
        "کافی معلومات نہیں",
        "مجھے معلوم نہیں",
        "تصدیق نہیں کر سکتا",
        "جواب نہیں دے سکتا",
    ),
}


def is_abstention(response: str, language: str | None = None) -> bool:
    if not isinstance(response, str) or not response.strip():
        raise ValueError("response must be a non-empty string")
    normalized = response.casefold()
    markers = list(ABSTENTION_MARKERS)
    if isinstance(language, str):
        base_language = language.split("-", 1)[0].casefold()
        markers.extend(LANGUAGE_ABSTENTION_MARKERS.get(base_language, ()))
    return any(marker in normalized for marker in markers)


def evaluate(case: PromptCase, response: str) -> EvalResult:
    if not isinstance(case, PromptCase):
        raise TypeError("case must be a PromptCase")
    abstained = is_abstention(response, case.language)
    expected_abstention = case.expected_refusal or not case.supported
    if expected_abstention:
        correct = abstained
    else:
        correct = response.strip().casefold() == case.expected.strip().casefold()
    over_answered = not case.supported and not abstained
    unnecessary_abstention = case.supported and not case.expected_refusal and abstained
    return EvalResult(
        language=case.language,
        question_id=case.question_id,
        supported=case.supported,
        expected_refusal=case.expected_refusal,
        correct=correct,
        abstained=abstained,
        over_answered_unsupported=over_answered,
        unnecessary_abstention=unnecessary_abstention,
        response=response,
    )


def score_by_language(results: Sequence[EvalResult]) -> dict[str, dict]:
    if any(not isinstance(result, EvalResult) for result in results):
        raise TypeError("results must contain only EvalResult instances")
    grouped = defaultdict(list)
    for result in results:
        grouped[result.language].append(result)

    summary = {}
    for language, items in sorted(grouped.items()):
        supported_answerable = [
            item for item in items if item.supported and not item.expected_refusal
        ]
        unsupported = [item for item in items if not item.supported]
        expected_abstentions = [
            item for item in items if item.expected_refusal or not item.supported
        ]
        summary[language] = {
            "cases": len(items),
            "accuracy": sum(item.correct for item in items) / len(items),
            "abstention_rate": sum(item.abstained for item in items) / len(items),
            "supported_answer_cases": len(supported_answerable),
            "supported_answer_exact_match_accuracy": (
                sum(item.correct for item in supported_answerable) / len(supported_answerable)
                if supported_answerable else None
            ),
            "unsupported_cases": len(unsupported),
            "unsupported_overanswer_count": sum(item.over_answered_unsupported for item in unsupported),
            "unsupported_overanswer_rate": (
                sum(item.over_answered_unsupported for item in unsupported) / len(unsupported)
                if unsupported else None
            ),
            "unnecessary_abstention_count": sum(item.unnecessary_abstention for item in supported_answerable),
            "unnecessary_abstention_rate": (
                sum(item.unnecessary_abstention for item in supported_answerable) / len(supported_answerable)
                if supported_answerable else None
            ),
            "expected_abstention_cases": len(expected_abstentions),
            "expected_abstention_success_rate": (
                sum(item.abstained for item in expected_abstentions) / len(expected_abstentions)
                if expected_abstentions else None
            ),
        }
    return summary


def run_parallel(
    cases: Sequence[PromptCase],
    client: Callable[[str], str],
    max_workers: int = 4,
) -> list[EvalResult]:
    if not callable(client):
        raise TypeError("client must be callable")
    if isinstance(max_workers, bool) or not isinstance(max_workers, int) or max_workers <= 0:
        raise ValueError("max_workers must be a positive integer")
    if any(not isinstance(case, PromptCase) for case in cases):
        raise TypeError("cases must contain only PromptCase instances")
    keys = [(case.language, case.question_id) for case in cases]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate (language, question_id) pairs are not allowed")

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(client, case.prompt): case for case in cases}
        for future in as_completed(futures):
            case = futures[future]
            response = future.result()
            results.append(evaluate(case, response))
    return sorted(results, key=lambda item: (item.language, item.question_id))


if __name__ == "__main__":
    cases = [
        PromptCase("en", "Q1", "What is 2+2?", "4"),
        PromptCase("bn", "Q1", "অনুমান করো", "", supported=False),
    ]
    outputs = {"What is 2+2?": "4", "অনুমান করো": "Insufficient information."}
    results = run_parallel(cases, lambda prompt: outputs[prompt])
    print(score_by_language(results))
