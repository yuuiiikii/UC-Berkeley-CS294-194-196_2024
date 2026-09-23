# Minimal ReAct-style time agent

问题只有一句，“北京现在几点？”没有 Tool 时，Policy 应该承认缺少 current state。开放 `get_current_time` 后，它可以把 Observation 写进 answer。第三个 scenario 故意返回错误时间，格式和 timezone label 都保持正常。

`react.py` 使用 deterministic `ScriptedTimePolicy`，没有连接 LLM API。`ToolRegistry` 负责校验和执行 Action，`Agent` controller 把 Observation 写回 history。以后接真实 model 时只需要替换 `Policy.decide()`，现有 loop 可以继续用。

输出里的 `Thought` 是 controller 用的简短 decision note，方便看 control flow。

## Run

运行全部 scenario：

```bash
python3 experiments/react/react.py --scenario all
```

使用和 `results.md` 相同的 fixed clock：

```bash
python3 experiments/react/react.py \
  --scenario all \
  --fixed-now 2026-09-22T17:30:00+08:00
```

也可以单独运行：

```bash
python3 experiments/react/react.py --scenario no-tools
python3 experiments/react/react.py --scenario one-call
python3 experiments/react/react.py --scenario faulty-tool
```

`no-tools` 不暴露时间 Tool。`one-call` 允许调用一次，并把返回值用于 answer。`faulty-tool` 同样只调用一次，但 Tool 会把时间减去 8 小时，Policy 没有第二个 source 可以 cross-check。

mock policy 已经知道该请求 `Asia/Shanghai`。我把这部分固定下来，只看 tool result 怎样进入下一轮 decision，结果在 [results.md](results.md)。
