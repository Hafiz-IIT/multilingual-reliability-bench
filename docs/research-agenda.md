# Research agenda

## Central question
**When task semantics are held constant, how much do correctness, abstention, and unsupported-answer behavior change across languages?**

## Hypotheses
### H1
Matched multilingual tasks can reveal reliability gaps hidden by aggregate accuracy.

### H2
Abstention rate can vary independently of exact-match accuracy across languages.

### H3
Unicode-naive preprocessing can itself create false evaluation gaps.

## Proposed experiments
1. Build a parallel 3-language task set with native-speaker verification and evaluate several model versions.
2. Separate translation errors from reasoning errors using bilingual adjudication.
3. Compare exact match with semantic scoring and human review on the same cases.

## Metrics
- accuracy by language
- coverage/abstention by language
- unsupported-answer rate
- reference-language accuracy gap
- inter-rater agreement for human review

## Historical paper lineage
- **Human-Centered AI Design for Inclusive Digital Platforms**
- **Fairness and Bias in Large-Scale AI Models: A Comparative Analysis**

These are preserved from earlier research planning and are not publication claims.

## Preprint gate
Do not label a direction as a paper result until the protocol is frozen, baselines are reproduced, results include uncertainty/error analysis, negative cases are documented, and limitations are explicit.
