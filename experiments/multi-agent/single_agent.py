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
class Result:
    task: str
    answer: str
    estimated_latency_ms: float
    model_calls: int
    estimated_model_latency_ms: int


TASKS = (
    Task("trap", hit_rate=0.8, lookup_ms=5, backend_ms=100, threshold_ms=24.5),
    Task("clear", hit_rate=0.9, lookup_ms=5, backend_ms=100, threshold_ms=20),
)


class MockSingleAgent:
    """A deterministic one-pass policy, not an actual LLM."""

    def __init__(self) -> None:
        self.calls = 0

    def answer(self, task: Task) -> Result:
        self.calls += 1
        miss_rate = 1 - task.hit_rate

        # This one-pass shortcut forgets that misses also pay lookup cost.
        estimate = task.hit_rate * task.lookup_ms + miss_rate * task.backend_ms
        decision = "yes" if estimate < task.threshold_ms else "no"
        return Result(
            task=task.name,
            answer=f"{decision}; one-pass estimate is {estimate:.1f} ms",
            estimated_latency_ms=estimate,
            model_calls=self.calls,
            estimated_model_latency_ms=self.calls * MODEL_LATENCY_MS,
        )


def parse_scenarios(value: str) -> tuple[Task, ...]:
    if value == "all":
        return TASKS
    return tuple(task for task in TASKS if task.name == value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Single-agent mock baseline")
    parser.add_argument("--scenario", choices=("trap", "clear", "all"), default="all")
    args = parser.parse_args()

    for index, task in enumerate(parse_scenarios(args.scenario)):
        if index:
            print()
        agent = MockSingleAgent()
        result = agent.answer(task)
        print(f"=== {task.name} ===")
        print(f"Question: {task.question}")
        print(f"Answer: {result.answer}")
        print(f"Model calls: {result.model_calls}")
        print(f"Estimated model latency: {result.estimated_model_latency_ms} ms")


if __name__ == "__main__":
    main()
