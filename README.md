# Multilingual Reliability Bench

A lightweight benchmark scaffold for comparing answer reliability across languages without pretending that translation equivalence guarantees reasoning equivalence.

## Implemented
- normalized exact-match scoring
- abstention tracking
- unsupported-answer flagging
- per-language accuracy / coverage summaries
- gap calculation against a reference language
- synthetic examples for English, Bengali and Hindi
- deterministic tests

## Run
```bash
python -m unittest discover -s tests -v
python multilingual_reliability_bench.py
```

## Scope and limitations
This repository is an evaluation scaffold, not a claim of a representative multilingual safety benchmark. The included cases are synthetic and intentionally small. A serious study should add native-speaker review, larger task families, model/version metadata and confidence intervals.
