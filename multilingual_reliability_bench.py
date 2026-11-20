from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
import unicodedata


ABSTAIN_MARKERS = {"", "abstain", "unknown", "insufficient evidence", "জানি না", "पता नहीं"}


def normalize(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    text = unicodedata.normalize("NFKC", text.strip().casefold())
    text = "".join(
        ch for ch in text
        if ch.isalnum() or ch.isspace() or unicodedata.category(ch).startswith("M")
    )
    return " ".join(text.split())


@dataclass(frozen=True)
class Case:
    case_id: str
    language: str
    expected: str
    response: str
    supported: bool = True

    def __post_init__(self):
        if not isinstance(self.case_id, str) or not self.case_id.strip():
            raise ValueError("case_id must be non-empty")
        if not isinstance(self.language, str) or not self.language.strip():
            raise ValueError("language must be non-empty")
        if not isinstance(self.expected, str) or not isinstance(self.response, str):
            raise ValueError("expected and response must be strings")
        if not isinstance(self.supported, bool):
            raise ValueError("supported must be boolean")


@dataclass(frozen=True)
class Metrics:
    language: str
    total: int
    correct: int
    abstained: int
    unsupported: int
    supported_total: int
    unsupported_non_abstain: int

    @property
    def accuracy(self) -> float:
        return self.correct / self.supported_total if self.supported_total else 0.0

    @property
    def coverage(self) -> float:
        return (self.supported_total - self.abstained) / self.supported_total if self.supported_total else 0.0


def is_abstention(text: str) -> bool:
    return normalize(text) in {normalize(x) for x in ABSTAIN_MARKERS}


def evaluate(cases: list[Case]) -> dict[str, Metrics]:
    if not isinstance(cases, list) or any(not isinstance(case, Case) for case in cases):
        raise ValueError("cases must be a list of Case values")
    keys = [(case.case_id, case.language) for case in cases]
    if len(keys) != len(set(keys)):
        raise ValueError("case_id/language pairs must be unique")
    buckets = defaultdict(lambda: {
        "total": 0, "correct": 0, "abstained": 0, "unsupported": 0,
        "supported_total": 0, "unsupported_non_abstain": 0,
    })
    for case in cases:
        b = buckets[case.language]
        b["total"] += 1
        if not case.supported:
            b["unsupported"] += 1
            if not is_abstention(case.response):
                b["unsupported_non_abstain"] += 1
            # Unsupported language/model combinations are reported separately;
            # they must not inflate or depress supported-language accuracy.
            continue
        b["supported_total"] += 1
        if is_abstention(case.response):
            b["abstained"] += 1
        elif normalize(case.response) == normalize(case.expected):
            b["correct"] += 1

    return {
        lang: Metrics(lang, **values)
        for lang, values in sorted(buckets.items())
    }


def accuracy_gap(metrics: dict[str, Metrics], reference: str = "en") -> dict[str, float]:
    if reference not in metrics:
        raise KeyError(f"reference language {reference!r} missing")
    if metrics[reference].supported_total == 0:
        raise ValueError(f"reference language {reference!r} has no supported cases")
    ref = metrics[reference].accuracy
    return {lang: round(ref - m.accuracy, 6)
            for lang, m in metrics.items()
            if lang != reference and m.supported_total > 0}


if __name__ == "__main__":
    demo = [
        Case("1", "en", "Delhi", "Delhi"),
        Case("1", "bn", "দিল্লি", "দিল্লি"),
        Case("1", "hi", "दिल्ली", "पता नहीं"),
    ]
    results = evaluate(demo)
    print(results)
    print("accuracy gaps:", accuracy_gap(results))
