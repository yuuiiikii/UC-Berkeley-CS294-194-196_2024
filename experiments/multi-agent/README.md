# Single-agent and multi-agent comparison

题目是算 cache 的 expected latency。`single_agent.py` 直接算一次并给出 yes/no。`multi_agent.py` 里的 analyst 先用同样的公式，checker 会重新检查 cache miss 的路径，最后由 answerer 整理结果。

两个脚本都用 deterministic mock model，没有请求 LLM API。checker 修正公式的行为直接写在代码里，这里看的就是 control flow。每次 mock call 记作 `120 ms`，多出来的调用会直接显示在结果里。

## Run

```bash
python3 experiments/multi-agent/single_agent.py --scenario all
python3 experiments/multi-agent/multi_agent.py --scenario all
```

`trap` 把 threshold 放在两个计算结果之间。漏掉 cache miss 也要支付 lookup cost，答案就会从 no 算成 yes。`clear` 也有同样的计算错误，只是没有改变最后判断。

脚本会打印 answer、model calls 和 estimated model latency，结果记在 [results.md](results.md)。
