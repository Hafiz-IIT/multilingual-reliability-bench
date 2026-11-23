from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from multilingual_reliability_bench import PromptCase, evaluate, score_by_language


@dataclass(frozen=True)
class ParallelCase:
    case_id: str
    prompt_by_language: Mapping[str, str]
    expected_by_language: Mapping[str, str]
    response_by_language: Mapping[str, str]
    supported_by_language: Mapping[str, bool] = field(default_factory=dict)
    expected_refusal_by_language: Mapping[str, bool] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ValueError("case_id must be a non-empty string")
        keys = set(self.prompt_by_language)
        if not keys or keys != set(self.expected_by_language) or keys != set(self.response_by_language):
            raise ValueError("prompt, expected and response mappings must contain the same non-empty languages")
        if self.supported_by_language and set(self.supported_by_language) != keys:
            raise ValueError("supported_by_language must cover every language")
        if self.expected_refusal_by_language and set(self.expected_refusal_by_language) != keys:
            raise ValueError("expected_refusal_by_language must cover every language")

    def flatten(self) -> list[tuple[PromptCase, str]]:
        rows = []
        for language in sorted(self.prompt_by_language):
            supported = self.supported_by_language.get(language, True)
            expected_refusal = self.expected_refusal_by_language.get(language, False)
            case = PromptCase(
                language=language,
                question_id=self.case_id,
                prompt=self.prompt_by_language[language],
                expected=self.expected_by_language[language],
                supported=supported,
                expected_refusal=expected_refusal,
            )
            response = self.response_by_language[language]
            if not isinstance(response, str) or not response.strip():
                raise ValueError(f"response for {language} must be a non-empty string")
            rows.append((case, response))
        return rows


def evaluate_parallel(cases: list[ParallelCase]) -> dict:
    if any(not isinstance(case, ParallelCase) for case in cases):
        raise TypeError("cases must contain only ParallelCase instances")
    ids = [case.case_id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate parallel case IDs are not allowed")
    flattened = [pair for case in cases for pair in case.flatten()]
    results = [evaluate(case, response) for case, response in flattened]
    metrics = score_by_language(results)
    accuracies = [value["accuracy"] for value in metrics.values()]
    answer_rates = [1.0 - value["abstention_rate"] for value in metrics.values()]
    unsupported_rates = [
        value["unsupported_overanswer_rate"]
        for value in metrics.values()
        if value["unsupported_overanswer_rate"] is not None
    ]
    return {
        "metrics": metrics,
        "accuracy_range": max(accuracies) - min(accuracies) if accuracies else 0.0,
        "answer_rate_range": max(answer_rates) - min(answer_rates) if answer_rates else 0.0,
        "coverage_range": max(answer_rates) - min(answer_rates) if answer_rates else 0.0,
        "unsupported_overanswer_rate_range": (
            max(unsupported_rates) - min(unsupported_rates) if unsupported_rates else None
        ),
        "results": results,
    }


if __name__ == "__main__":
    example = [
        ParallelCase(
            "capital",
            {"en": "What is the capital of India?", "bn": "ভারতের রাজধানী কী?", "hi": "भारत की राजधानी क्या है?"},
            {"en": "Delhi", "bn": "দিল্লি", "hi": "दिल्ली"},
            {"en": "Delhi", "bn": "দিল্লি", "hi": "मुझे नहीं पता"},
        )
    ]
    print(evaluate_parallel(example))
