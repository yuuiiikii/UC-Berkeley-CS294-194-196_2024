# Lecture 01: LLM Reasoning

- **Course:** CS 194/294-196 Large Language Model Agents
- **Date:** September 9, 2024
- **Topic:** LLM reasoning
- **Reference:** https://rdi.berkeley.edu/llm-agents/f24

## One-Sentence Summary

Reasoning in LLM agents is best understood as a combination of representation, intermediate computation, and feedback: a model may produce useful intermediate steps, but reliable performance requires evaluation and correction mechanisms that are not identical to the original generation step.

## Core Concepts

### 1. Eliciting intermediate computation

Chain-of-thought-style prompting asks a model to produce intermediate steps before its final answer. This can make some multi-step tasks easier by turning one difficult mapping into a sequence of smaller mappings. The improvement is task-dependent, and the generated trace should not be treated as a formal proof.

Useful distinctions:

- **Answer accuracy:** whether the final answer is correct.
- **Trace consistency:** whether the intermediate steps support the answer.
- **Process faithfulness:** whether the trace reflects the computation that caused the answer.
- **Cost:** additional tokens, latency, and possible exposure of sensitive intermediate content.

### 2. Serial reasoning

A serial problem contains dependencies between steps. If step `t + 1` needs a correct result from step `t`, then an early error can make later reasoning internally consistent but globally wrong. This is one reason that agent systems need checkpoints, structured state, and targeted verification rather than only a larger output budget.

### 3. Premise order and task representation

Small changes to the order or presentation of premises can change model behavior. This is an evaluation warning: a benchmark result may partly measure sensitivity to formatting, ordering, or prompt conventions. Robust evaluation should vary irrelevant surface features and report the protocol precisely.

### 4. Self-correction

A self-correction loop typically looks like:

```text
answer = generate(problem)
critique = review(problem, answer)
answer2 = revise(problem, answer, critique)
```

The loop is not automatically reliable. If generation and review share the same blind spot, the second pass may preserve the original error. Correction becomes more credible when the review step has an independent test, external evidence, a different model or prompt, a tool call, or an executable check.

## Agent Design Implications

- Keep intermediate state structured where possible instead of relying on an unbounded transcript.
- Give each tool a narrow contract and validate its outputs before feeding them back into the loop.
- Use independent checks for claims that affect safety, money, access control, or irreversible actions.
- Log failed attempts and correction decisions so that evaluation can measure recovery, not only success cases.
- Report accuracy together with latency, token usage, tool calls, and failure modes.

## Evaluation Checklist

1. Is the task genuinely multi-step, or can it be solved by retrieval or pattern matching?
2. Does the benchmark randomize premise order and irrelevant wording?
3. Is the verifier independent from the generator?
4. Are intermediate traces evaluated for correctness, or only the final answer?
5. Are abstention and uncertainty allowed?
6. Does the system improve on hard cases, or only rewrite easy cases?

## Reflection Draft

The lecture made me less interested in treating “reasoning” as a single model feature. For an agent, reasoning is a workflow with inputs, intermediate state, checks, and recovery. A strong demo can hide errors if it reports only successful final answers; a stronger evaluation asks how the system behaves when the first plan is wrong, a tool returns unexpected data, or the premises are reordered.

## Follow-Up

- Read the focused notes in [llm-self-correction/notes.md](../llm-self-correction/notes.md).
- Add an actual lab or experiment only after recording the prompt, model, data, baseline, metrics, and failure cases.
- Keep personal observations separate from claims supported by the papers.