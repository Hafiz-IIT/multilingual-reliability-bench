# Status

## Implemented
- paired multilingual prompt-case schema with explicit supported/unsupported and expected-refusal labels
- exact-match scoring for supported answerable cases
- explicit abstention scoring for unsupported and refusal-required cases
- separate unsupported over-answer and unnecessary-abstention metrics
- per-language coverage and abstention summaries
- duplicate case-key validation and deterministic result ordering
- parallel client adapter with input validation
- regression tests + GitHub Actions CI

## Evaluation boundary
Abstention detection is a transparent phrase heuristic, and supported-answer scoring is exact-match only. These metrics are a benchmark scaffold, not semantic equivalence evaluation, calibrated reliability, or evidence of model parity across languages.

## Not claimed
- measured Bengali/Hindi/English capability parity
- human-validated translation or semantic labels
- broad cultural or dialect coverage
- production model reliability
- causal explanation for cross-language performance gaps
