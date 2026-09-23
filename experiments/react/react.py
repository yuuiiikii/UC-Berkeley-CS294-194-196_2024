from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Protocol, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class Decision:
    thought: str
    tool_call: ToolCall | None = None
    answer: str | None = None

    def __post_init__(self) -> None:
        if (self.tool_call is None) == (self.answer is None):
            raise ValueError("A decision must contain exactly one tool call or answer")


@dataclass(frozen=True)
class Observation:
    tool_name: str
    payload: dict[str, Any]


class Policy(Protocol):
    def decide(
        self,
        question: str,
        history: Sequence[Observation],
        available_tools: set[str],
    ) -> Decision: ...


class ScriptedTimePolicy:
    """A deterministic stand-in used to inspect the Agent loop.

    It emits short decision notes, not hidden chain-of-thought. Replace this class
    with an LLM-backed Policy to test model behavior.
    """

    def decide(
        self,
        question: str,
        history: Sequence[Observation],
        available_tools: set[str],
    ) -> Decision:
        del question

        if not history:
            if "get_current_time" not in available_tools:
                return Decision(
                    thought="The question needs current external state, but no time tool is available.",
                    answer="我现在没有可用的时间工具，不能可靠回答北京当前时间。",
                )
            return Decision(
                thought="I need a current time observation for Asia/Shanghai.",
                tool_call=ToolCall(
                    name="get_current_time",
                    arguments={"timezone": "Asia/Shanghai"},
                ),
            )

        latest = history[-1].payload
        if latest.get("status") != "ok":
            return Decision(
                thought="The time tool failed, and there is no independent observation to use.",
                answer="时间工具调用失败，我无法确认北京当前时间。",
            )

        return Decision(
            thought="I have one time observation and will answer from it.",
            answer=f"北京现在是 {latest['display_time']}。",
        )


class TimeTool:
    def __init__(
        self,
        fixed_now: datetime | None = None,
        fault_offset: timedelta = timedelta(0),
    ) -> None:
        self.fixed_now = fixed_now
        self.fault_offset = fault_offset

    def __call__(self, arguments: dict[str, Any]) -> dict[str, Any]:
        timezone_name = arguments.get("timezone")
        if not isinstance(timezone_name, str):
            return {"status": "error", "message": "timezone must be a string"}

        try:
            timezone = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError:
            return {"status": "error", "message": f"unknown timezone: {timezone_name}"}

        if self.fixed_now is None:
            current = datetime.now(timezone)
        else:
            current = self.fixed_now.astimezone(timezone)

        reported = current + self.fault_offset
        return {
            "status": "ok",
            "timezone": timezone_name,
            "iso": reported.isoformat(timespec="seconds"),
            "display_time": reported.strftime("%Y-%m-%d %H:%M:%S %Z (UTC%z)"),
        }


class ToolRegistry:
    def __init__(self, time_tool: TimeTool | None) -> None:
        self._tools = {"get_current_time": time_tool} if time_tool else {}

    @property
    def names(self) -> set[str]:
        return set(self._tools)

    def call(self, call: ToolCall) -> Observation:
        tool = self._tools.get(call.name)
        if tool is None:
            return Observation(
                tool_name=call.name,
                payload={"status": "error", "message": "tool is unavailable"},
            )
        return Observation(tool_name=call.name, payload=tool(call.arguments))


@dataclass(frozen=True)
class RunResult:
    answer: str
    tool_calls: int


class Agent:
    def __init__(
        self,
        policy: Policy,
        tools: ToolRegistry,
        max_tool_calls: int,
        max_steps: int = 4,
    ) -> None:
        self.policy = policy
        self.tools = tools
        self.max_tool_calls = max_tool_calls
        self.max_steps = max_steps

    def run(self, question: str) -> RunResult:
        history: list[Observation] = []
        tool_calls = 0
        print(f"Question: {question}")

        for _ in range(self.max_steps):
            available_tools = (
                self.tools.names if tool_calls < self.max_tool_calls else set()
            )
            decision = self.policy.decide(question, history, available_tools)
            print(f"Thought: {decision.thought}")

            if decision.answer is not None:
                print(f"Answer: {decision.answer}")
                return RunResult(answer=decision.answer, tool_calls=tool_calls)

            assert decision.tool_call is not None
            print(
                "Action: "
                f"{decision.tool_call.name}({json.dumps(decision.tool_call.arguments)})"
            )
            observation = self.tools.call(decision.tool_call)
            history.append(observation)
            tool_calls += 1
            print(f"Observation: {json.dumps(observation.payload, ensure_ascii=False)}")

        answer = "Agent stopped after reaching the step limit."
        print(f"Answer: {answer}")
        return RunResult(answer=answer, tool_calls=tool_calls)


SCENARIOS = ("no-tools", "one-call", "faulty-tool")


def parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError("--fixed-now must include a UTC offset")
    return parsed


def build_agent(scenario: str, fixed_now: datetime | None) -> Agent:
    if scenario == "no-tools":
        return Agent(
            policy=ScriptedTimePolicy(),
            tools=ToolRegistry(time_tool=None),
            max_tool_calls=0,
        )

    fault_offset = timedelta(hours=-8) if scenario == "faulty-tool" else timedelta(0)
    return Agent(
        policy=ScriptedTimePolicy(),
        tools=ToolRegistry(
            time_tool=TimeTool(fixed_now=fixed_now, fault_offset=fault_offset)
        ),
        max_tool_calls=1,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="A minimal ReAct-style time agent")
    parser.add_argument(
        "--scenario",
        choices=(*SCENARIOS, "all"),
        default="all",
    )
    parser.add_argument(
        "--fixed-now",
        help="ISO datetime with UTC offset, used for reproducible runs",
    )
    parser.add_argument("--question", default="北京现在几点？")
    args = parser.parse_args()

    fixed_now = parse_datetime(args.fixed_now)
    scenarios = SCENARIOS if args.scenario == "all" else (args.scenario,)

    for index, scenario in enumerate(scenarios):
        if index:
            print()
        print(f"=== {scenario} ===")
        agent = build_agent(scenario, fixed_now)
        agent.run(args.question)


if __name__ == "__main__":
    main()
