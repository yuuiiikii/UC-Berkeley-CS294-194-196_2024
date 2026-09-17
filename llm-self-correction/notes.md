# Reading Record: LLM Self-Correction

## Paper

**Large Language Models Cannot Self-Correct Reasoning Yet**

This paper was listed in the first-week reading set for Berkeley's CS 194/294-196 course. The notes below summarize the problem and its implications for agent design; they do not reproduce the paper.

## Main Question

Can a language model reliably find and fix its own reasoning errors when it is asked to review an answer without receiving new external information?

## Central Takeaway

A second generation pass is not the same thing as an independent verification process. If the model's critique uses the same assumptions, knowledge gaps, and heuristics as the original answer, it may fail to detect the original error or may introduce a new one. Self-correction should therefore be treated as an empirical procedure whose benefit must be measured against a baseline, not assumed from the presence of a “review your answer” prompt.

## Failure Modes to Watch

### Correlated mistakes

The generator and critic can share the same mistaken premise. In that case, the critique may sound plausible while validating the wrong path.

### No new evidence

If the correction step receives only the model's own previous text, it may have no information that allows it to resolve uncertainty.

### Confidence without calibration

A revised answer can be more fluent or more detailed without being more accurate. Surface confidence is not evidence of correction.

### Evaluation leakage

If the prompt or evaluator strongly hints at the expected answer, a reported improvement may reflect test-specific prompting rather than a general correction ability.

## A Useful Experimental Decomposition

To study a correction loop, compare at least these conditions:

1. Direct answer, one pass.
2. Deliberation or structured reasoning, one pass.
3. Self-critique followed by revision.
4. Revision with an external verifier, retrieved evidence, or executable test.
5. Revision with an independent model or independently sampled critique.

For every condition, record final accuracy, correction rate on initially wrong answers, regression rate on initially correct answers, token usage, latency, and the types of errors that remain.

## Minimal Pseudocode

```python
first = generate(problem)

if use_self_critique:
    critique = generate_critique(problem, first)
    revised = revise(problem, first, critique)
else:
    revised = first

if use_external_check:
    check = verify(revised)
    revised = repair_or_abstain(revised, check)
```

The important design question is what `verify` knows that `generate` did not. If the answer is “nothing,” the loop may still be useful, but its reliability must be demonstrated rather than inferred.

## Agent Engineering Lessons

- Prefer verifiers with a different failure profile from the generator.
- Use tools for arithmetic, code execution, retrieval, schema validation, and other checks that do not depend only on fluent text generation.
- Preserve the original answer and critique in logs so that regressions are visible.
- Permit abstention when the system cannot obtain enough evidence.
- Evaluate correction on both wrong and correct initial answers; otherwise a method can appear successful by changing answers indiscriminately.

## Reflection Draft

The paper is a useful warning against a common agent pattern: ask the model to answer, then ask the same model whether it is sure. That pattern can improve presentation, but it does not automatically create a source of truth. My practical rule after reading it is to ask what new evidence enters the loop at each correction step. If no new evidence enters, the procedure should be called self-review rather than verification, and its gains should be reported with regression cases.

## Open Questions

- How much independence is enough for a verifier to be useful?
- When does tool-based checking cost more than the errors it prevents?
- Can training produce reliable internal critics, or will external feedback remain necessary for high-stakes tasks?
- How should an agent communicate uncertainty when critique and evidence disagree?

## Status

This is a reading record and design analysis. It contains no claim of a completed course experiment or submitted assignment.