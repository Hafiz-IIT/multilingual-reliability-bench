from __future__ import annotations

from dataclasses import dataclass
from multilingual_reliability_bench import Case, evaluate


@dataclass(frozen=True)
class ParallelCase:
    case_id: str
    expected_by_language: dict[str, str]
    response_by_language: dict[str, str]
    supported_by_language: dict[str, bool] | None = None

    def flatten(self) -> list[Case]:
        languages = set(self.expected_by_language) | set(self.response_by_language)
        if self.supported_by_language is not None and set(self.supported_by_language) - languages:
            raise ValueError("support flags reference languages absent from the parallel case")
        if self.supported_by_language is not None and any(not isinstance(v, bool) for v in self.supported_by_language.values()):
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
    flat = [row for case in cases for row in case.flatten()]
    metrics = evaluate(flat)
    accuracies = [m.accuracy for m in metrics.values()]
    coverages = [m.coverage for m in metrics.values()]
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
