from __future__ import annotations

from dataclasses import dataclass
from multilingual_reliability_bench import Case, evaluate


@dataclass(frozen=True)
class ParallelCase:
    case_id: str
    expected_by_language: dict[str, str]
    response_by_language: dict[str, str]
    supported_by_language: dict[str, bool] | None = None

    def __post_init__(self):
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ValueError("case_id must be non-empty")
        object.__setattr__(self, "case_id", self.case_id.strip())

    def flatten(self) -> list[Case]:
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ValueError("case_id must be non-empty")
        if not isinstance(self.expected_by_language, dict) or not isinstance(self.response_by_language, dict):
            raise ValueError("parallel expected/response values must be dictionaries")
        for mapping in (self.expected_by_language, self.response_by_language):
            if any(not isinstance(language, str) or not language.strip() for language in mapping):
                raise ValueError("language keys must be non-empty strings")
        languages = set(self.expected_by_language) | set(self.response_by_language)
        if self.supported_by_language is not None:
            if not isinstance(self.supported_by_language, dict):
                raise ValueError("supported_by_language must be a dictionary")
            if any(not isinstance(language, str) or not language.strip() for language in self.supported_by_language):
                raise ValueError("support-flag language keys must be non-empty strings")
            if set(self.supported_by_language) - languages:
                raise ValueError("support flags reference languages absent from the parallel case")
            if any(not isinstance(v, bool) for v in self.supported_by_language.values()):
                raise ValueError("language support flags must be booleans")
        rows: list[Case] = []
        for language in sorted(languages):
            if language not in self.expected_by_language or language not in self.response_by_language:
                raise ValueError(f"incomplete parallel case for {language}")
            rows.append(
                Case(
                    self.case_id,
                    language,
                    self.expected_by_language[language],
                    self.response_by_language[language],
                    supported=(self.supported_by_language or {}).get(language, True),
                )
            )
        return rows


def evaluate_parallel(cases: list[ParallelCase]) -> dict:
    if not isinstance(cases, list) or any(not isinstance(case, ParallelCase) for case in cases):
        raise ValueError("cases must be a list of ParallelCase values")
    ids = [case.case_id for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("parallel case IDs must be unique")
    flat = [row for case in cases for row in case.flatten()]
    metrics = evaluate(flat)
    supported = [m for m in metrics.values() if m.supported_total > 0]
    accuracies = [m.accuracy for m in supported]
    coverages = [m.coverage for m in supported]
    return {
        "metrics": metrics,
        "accuracy_range": max(accuracies) - min(accuracies) if accuracies else 0.0,
        "coverage_range": max(coverages) - min(coverages) if coverages else 0.0,
    }


if __name__ == "__main__":
    example = [
        ParallelCase(
            "capital",
            {"en": "Delhi", "bn": "দিল্লি", "hi": "दिल्ली"},
            {"en": "Delhi", "bn": "দিল্লি", "hi": "पता नहीं"},
        )
    ]
    print(evaluate_parallel(example))
