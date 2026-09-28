# Evaluation Protocol

## Primary research question
Do comparable tasks show systematic differences in correctness, unsupported answering, or abstention across languages?

## Metrics
- Accuracy by language
- Coverage by language
- Unsupported-answer rate
- Reference-language accuracy gap
- Reviewer agreement

## Falsification criteria
- Metrics change because normalization corrupts text.
- Parallel cases are not semantically equivalent.
- Unsupported answers are hidden by aggregate accuracy.

## Reproducibility
```bash
python -m unittest discover -s tests -v
```
