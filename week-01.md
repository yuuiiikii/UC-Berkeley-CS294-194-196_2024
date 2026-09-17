# Week 01: LLM Reasoning

> Fall 2024 course archive. This is an independently organized learning record, not an official Berkeley course handout.

## Session

- Course: CS 194/294-196, Large Language Model Agents
- Date: September 9, 2024
- Theme: LLM reasoning
- Course page: https://rdi.berkeley.edu/llm-agents/f24

## What This Week Focused On

The first week framed reasoning as a capability that an LLM agent may need before it can plan, use tools, or complete multi-step tasks. The useful question is not only whether a model can produce a correct answer, but whether it can decompose a task, preserve intermediate constraints, detect a mistake, and revise its answer when new evidence is available.

The lecture and readings connected four ideas:

1. **Reasoning traces and prompting.** A model can often perform better when it is encouraged to expose intermediate steps, but a visible chain of thought is not a guarantee of correctness or a faithful description of the model's internal computation.
2. **Serial tasks.** Some problems require a sequence of dependent operations. A small error early in the sequence can propagate through every later step.
3. **Self-correction.** Asking a model to review its own answer is useful as a procedure, but the review step does not automatically provide an independent source of truth.
4. **Problem formulation.** Premise order, representation, and the exact evaluation protocol can change measured reasoning performance.

## Reading Notes

The syllabus listed the following readings for this week:

- *Chain-of-Thought Reasoning Without Prompting*
- *Large Language Models Cannot Self-Correct Reasoning Yet*
- *Premise Order Matters in Reasoning with Large Language Models*
- *Chain-of-Thought Empowers Transformers to Solve Inherently Serial Problems*

The common thread is that reasoning performance depends on more than model size. Prompt format, task structure, intermediate supervision, and the availability of reliable feedback all matter.

## Working Takeaways

- A reasoning trace is an interface for eliciting or inspecting behavior, not a proof.
- A longer answer can contain more opportunities for error; verbosity should not be confused with reliability.
- Self-review is strongest when the reviewer has new evidence, a different view of the problem, executable checks, or a reliable verifier.
- Agent evaluation should separate final-answer accuracy from process quality, tool-use correctness, recovery behavior, and cost.

## Reflection Draft

The most important shift in perspective this week was moving from “Can the model answer?” to “What information and feedback does the model have while it is solving the task?” An agent that only generates text may appear capable on short tasks, but longer workflows expose the need for state, verification, and recovery. This makes reasoning a systems problem as much as a prompting problem.

I also came away more cautious about self-correction claims. A second pass can improve an answer, but it can also repeat the same mistaken assumption with greater confidence. Any serious agent should make its sources of feedback explicit and should be evaluated on whether correction actually improves reliability rather than merely producing a different explanation.

## Questions to Carry Forward

- When does a reasoning trace improve task performance rather than only explanation quality?
- How can an evaluator distinguish genuine correction from a confident rewrite?
- Which agent tasks benefit most from external tools or executable checks?
- How should latency and token cost be reported alongside accuracy?

See [lecture-01/notes.md](lecture-01/notes.md) for detailed notes and [llm-self-correction/notes.md](llm-self-correction/notes.md) for the focused paper record.