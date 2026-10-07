# Multilingual Reliability Bench

<p align="center">
  <strong>Measuring Reliability Gaps Across Languages</strong><br/>
  <sub>Paired evaluation for correctness, abstention and unsupported answers.</sub>
</p>

<p align="center">
  <a href="https://github.com/Hafiz-IIT/multilingual-reliability-bench/actions"><img src="https://img.shields.io/github/actions/workflow/status/Hafiz-IIT/multilingual-reliability-bench/ci.yml?label=CI" alt="CI"/></a>
  <img src="https://img.shields.io/badge/status-research%20prototype-blue" alt="Research prototype"/>
  <img src="https://img.shields.io/badge/evaluation-paired%20cases-orange" alt="Paired evaluation"/>
</p>

## Research question

**Does a model behave equally reliably when the same semantic task is expressed in different languages?**

The benchmark is deliberately paired: the comparison is between equivalent task intent, not unrelated test sets.

## Evaluation pipeline

```
Paired cases
   ↓
Unicode-safe normalization
   ↓
Correct / abstain / unsupported labels
   ↓
Per-language metrics
   ↓
Reference-language gap analysis
```

## Try it

```bash
python multilingual_reliability_bench.py
python -m unittest discover -s tests -v
```

`paired_benchmark.py` provides deterministic paired cases and exposes measurable disparity rather than hiding it inside an aggregate score.

## Implemented

- Unicode-preserving normalization
- exact-match baseline
- abstention detection
- unsupported-answer tracking
- per-language metrics
- paired disparity analysis
- deterministic CI

## Research boundary

The included dataset is a benchmark scaffold, not a claim of comprehensive multilingual coverage or model-wide generalization.

Related work: [Agent Evidence Probes](https://github.com/Hafiz-IIT/agent-evidence-probes) · [Secure Document RAG Agent](https://github.com/Hafiz-IIT/secure-doc-rag-agent)
