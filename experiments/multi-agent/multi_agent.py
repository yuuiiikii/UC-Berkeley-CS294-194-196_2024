from __future__ import annotations

import argparse
from dataclasses import dataclass


MODEL_LATENCY_MS = 120


@dataclass(frozen=True)
class Task:
    name: str
    hit_rate: float
    lookup_ms: float
    backend_ms: float
    threshold_ms: float

    @property
    def question(self) -> str:
        return (
            f"Cache lookup costs {self.lookup_ms:g} ms. Backend work costs "
            f"{self.backend_ms:g} ms on a miss. Hit rate is {self.hit_rate:.0%}. "
            f"Is expected latency below {self.threshold_ms:g} ms?"
        )


@dataclass(frozen=True)
class Analysis:
    estimate_ms: float
    note: str


@dataclass(frozen=True)
class Check:
    estimate_ms: float
    decision: str
    note: str


TASKS = (
    Task("trap", hit_rate=0.8, lookup_ms=5, backend_ms=100, threshold_ms=24.5),
    Task("clear", hit_rate=0.9, lookup_ms=5, backend_ms=100, threshold_ms=20),
)


class MockMultiAgent:
    """Three deterministic role policies, not three real LLM agents."""

    def __init__(self) -> None:
        self.calls = 0

    def call_analyst(self, task: Task) -> Analysis:
        self.calls += 1
        miss_rate = 1 - task.hit_rate
        estimate = task.hit_rate * task.lookup_ms + miss_rate * task.backend_ms
        return Analysis(estimate, "The first estimate counts lookup only on hits.")

    def call_checker(self, task: Task, analysis: Analysis) -> Check:
        self.calls += 1
        miss_rate = 1 - task.hit_rate
        corrected = task.lookup_ms + miss_rate * task.backend_ms
        decision = "yes" if corrected < task.threshold_ms else "no"
        return Check(
            corrected,
            decision,
            f"Checker corrected {analysis.estimate_ms:.1f} ms to {corrected:.1f} ms.",
        )

    def call_answerer(self, task: Task, check: Check) -> str:
        self.calls += 1
        return f"{check.decision}; verified estimate is {check.estimate_ms:.1f} ms"


def parse_scenarios(value: str) -> tuple[Task, ...]:
    if value == "all":
        return TASKS
    return tuple(task for task in TASKS if task.name == value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Multi-agent mock comparison")
    parser.add_argument("--scenario", choices=("trap", "clear", "all"), default="all")
    args = parser.parse_args()

    for index, task in enumerate(parse_scenarios(args.scenario)):
        if index:
            print()
        system = MockMultiAgent()
        analysis = system.call_analyst(task)
        check = system.call_checker(task, analysis)
        answer = system.call_answerer(task, check)
        print(f"=== {task.name} ===")
        print(f"Question: {task.question}")
        print(f"Analyst: {analysis.estimate_ms:.1f} ms")
        print(f"Checker: {check.note}")
        print(f"Answerer: {answer}")
        print(f"Model calls: {system.calls}")
        print(f"Estimated model latency: {system.calls * MODEL_LATENCY_MS} ms")


if __name__ == "__main__":
    main()
