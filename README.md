# Multilingual Reliability Bench

> **Measure whether an AI system stays reliable when the language changes—even when the task does not.**

Multilingual systems may preserve fluency while changing accuracy, abstention behavior, or unsupported-answer rates across languages. This repository makes those differences explicit with a small, language-aware evaluation scaffold.

## Implemented

- Unicode-aware text normalization
- normalized exact-match scoring
- abstention detection
- unsupported-answer counting
- per-language accuracy and coverage
- reference-language gap calculation
- English/Bengali/Hindi synthetic test cases

## Repository map

| Path | Purpose |
|---|---|
| `multilingual_reliability_bench.py` | Core implementation |
| `tests/` | Deterministic tests |
| `examples/` | Reproducible synthetic/example case |
| `docs/architecture.md` | Architecture |
| `docs/research-agenda.md` | Experiments and research lineage |
| `STATUS.md` | Claims boundary and maturity |
| `CITATION.cff` | Citation metadata |

## Quick start

```bash
python -m unittest discover -s tests -v
python multilingual_reliability_bench.py
```

## Architecture

**multilingual cases → Unicode normalization → answer scoring → abstention/support checks → per-language metrics → cross-language gap**

## Research lineage

This work connects the user's multilingual background and AI-evaluation interests with the older research directions on human-centered AI and fairness/bias in large-scale AI models.

The historical titles named in this repository are research directions, not claims that those manuscripts have already been published.

## Evaluation direction

Expand from synthetic examples to matched task sets written or reviewed by native speakers; freeze prompts/model versions and report confidence intervals rather than anecdotal examples.

## Status

**Reproducible research prototype.** The current cases are synthetic and small. It is not a representative benchmark of Bengali, Hindi, English, or multilingual model safety.
