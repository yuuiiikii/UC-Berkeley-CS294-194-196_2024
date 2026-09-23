# Experiment results

下面的输出使用 fixed clock，方便重复运行。

```bash
python3 experiments/react/react.py \
  --scenario all \
  --fixed-now 2026-09-22T17:30:00+08:00
```

## no-tools

```text
Question: 北京现在几点？
Thought: The question needs current external state, but no time tool is available.
Answer: 我现在没有可用的时间工具，不能可靠回答北京当前时间。
```

Policy 没有 current state，也没有编一个时间。用户的问题没被回答，但行为是可预测的。

## one-call

```text
Question: 北京现在几点？
Thought: I need a current time observation for Asia/Shanghai.
Action: get_current_time({"timezone": "Asia/Shanghai"})
Observation: {"status": "ok", "timezone": "Asia/Shanghai", "iso": "2026-09-22T17:30:00+08:00", "display_time": "2026-09-22 17:30:00 CST (UTC+0800)"}
Thought: I have one time observation and will answer from it.
Answer: 北京现在是 2026-09-22 17:30:00 CST (UTC+0800)。
```

一次 Tool call 已经够用。第二轮 decision 读取 Observation 后直接回答。

## faulty-tool

```text
Question: 北京现在几点？
Thought: I need a current time observation for Asia/Shanghai.
Action: get_current_time({"timezone": "Asia/Shanghai"})
Observation: {"status": "ok", "timezone": "Asia/Shanghai", "iso": "2026-09-22T09:30:00+08:00", "display_time": "2026-09-22 09:30:00 CST (UTC+0800)"}
Thought: I have one time observation and will answer from it.
Answer: 北京现在是 2026-09-22 09:30:00 CST (UTC+0800)。
```

Tool 把时间减了 8 小时，字段和 timezone label 仍然正常。Policy 原样相信 Observation，answer 也跟着错。

格式正确的错误值比显式 error 难处理。第二个 clock source 或 UTC offset check 都能提供额外 signal，代价是再多一次调用和一段 failure path。
