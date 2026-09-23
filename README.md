# Learning LLM agents

I came to this course after an Agent internship and a few internal prototypes. One of them was a research assistant with query rewriting, hybrid retrieval, reranking, context packing, citation-aware generation, and a small tool router. I had also tried planner/executor/reviewer workflows and basic conversation-state management.

The weekly order follows [UC Berkeley CS 194/294-196: Large Language Model Agents](https://rdi.berkeley.edu/llm-agents/f24).

The systems worked well enough to demo, but some design choices were still based on habit. A reviewer sounded like an independent check even when it saw the same context. A tool call made a workflow look agentic even when the next step was fixed in code. This repository is where I slow those decisions down and test them in smaller examples.

Most notes are in Chinese because that is faster for me while learning. Technical terms, code, paths, and short project descriptions stay in English.

## Repository map

- `lectures/` contains my lecture notes.
- `readings/` contains paper notes and questions I have not settled yet.
- `experiments/` contains small runnable examples. They are intentionally narrower than full paper reproductions.
- `reflections/` records what changed after each week.
- `projects/` is reserved for work that grows beyond a small experiment.

This is a learning repository, not a polished implementation. Some conclusions will probably change as the course moves on.

## Progress

- Week 01: LLM reasoning and self-correction
- Week 02: Agent boundaries, ReAct, WebShop, and a minimal tool loop
- Week 03: AutoGen, StateFlow, and a small single-agent / multi-agent comparison
