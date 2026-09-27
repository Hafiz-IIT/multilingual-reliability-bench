from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
import re


ABSTAIN_MARKERS = {"", "abstain", "unknown", "insufficient evidence", "জানি না", "पता नहीं"}


def normalize(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s]", "", text, flags=re.UNICODE)
    return " ".join(text.split())


@dataclass(frozen=True)
class Case:
    case_id: str
    language: str
    expected: str
    response: str
    supported: bool = True


@dataclass(frozen=True)
class Metrics:
    language: str
    total: int
    correct: int
    abstained: int
    unsupported: int

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def coverage(self) -> float:
        return (self.total - self.abstained) / self.total if self.total else 0.0


def is_abstention(text: str) -> bool:
    return normalize(text) in {normalize(x) for x in ABSTAIN_MARKERS}


def evaluate(cases: list[Case]) -> dict[str, Metrics]:
    buckets = defaultdict(lambda: {"total": 0, "correct": 0, "abstained": 0, "unsupported": 0})
    for case in cases:
        b = buckets[case.language]
        b["total"] += 1
        if is_abstention(case.response):
            b["abstained"] += 1
        elif normalize(case.response) == normalize(case.expected):
            b["correct"] += 1
        if not case.supported and not is_abstention(case.response):
            b["unsupported"] += 1

    return {
        lang: Metrics(lang, **values)
        for lang, values in sorted(buckets.items())
    }


def accuracy_gap(metrics: dict[str, Metrics], reference: str = "en") -> dict[str, float]:
    if reference not in metrics:
        raise KeyError(f"reference language {reference!r} missing")
    ref = metrics[reference].accuracy
    return {lang: round(ref - m.accuracy, 6) for lang, m in metrics.items() if lang != reference}


if __name__ == "__main__":
    demo = [
        Case("1", "en", "Delhi", "Delhi"),
        Case("1", "bn", "দিল্লি", "দিল্লি"),
        Case("1", "hi", "दिल्ली", "पता नहीं"),
    ]
    results = evaluate(demo)
    print(results)
    print("accuracy gaps:", accuracy_gap(results))
