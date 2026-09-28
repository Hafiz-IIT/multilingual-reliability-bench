# Architecture

## Purpose
Benchmark scaffold for measuring answer reliability, abstention and unsupported-answer gaps across languages.

## Flow
Parallel multilingual cases → Unicode-safe normalization → correctness/abstention/support labels → per-language metrics → reference-language gap analysis.

## Invariants
1. Normalization must preserve language-specific combining marks.
2. Unsupported non-abstaining answers must be counted.
3. Language gaps must use the same task definition.

## Failure handling
Outputs should remain inspectable and expose the reason for allow, substitute, block, abstain, verify, or escalate decisions.
