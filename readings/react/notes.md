# Paper notes: ReAct

`Thought -> Action -> Observation` 在 Agent demo 里太常见了，我差点忽略论文还专门比较了 Reason-only 和 Act-only。那组对照比格式本身更能说明 ReAct 为什么有用。

## Reason-only 和 Act-only 卡在哪里

Chain-of-Thought 把 reasoning 留在 model context 里。模型可以拆任务、保存中间结论，可缺失或过时的事实不会自己进来。前面 hallucinate 了一个事实，后面还能沿着它继续推。

Act-only 会 search、click，也会改 Environment。论文分析 ALFWorld trajectory 时发现，这种 Agent 容易丢 current state，也不太会把目标拆成 subgoal。

ReAct 把两条 trajectory 插在一起。reasoning 选下一步 Action，Environment 返回 Observation，后面的 reasoning 再读新 state。

```text
Question
   |
Thought
   |
Action
   |
Observation
   |
Thought
   |
Action
   |
  ...
   |
Answer
```

论文里的 Thought 是 verbal reasoning trace。production Agent 没必要保存或展示完整 chain-of-thought。简短 plan、state summary 和 tool decision 已经足够调试，也更容易做权限控制。

## Action 之后真的多了什么

search 会带回模型参数里没有的事实，calculator 和 code execution 给出可复查的结果，click 或 write 则直接改变 Environment。empty result、invalid option、permission error 也有用，它们会迫使 plan 改道。

模型可以在 context 里猜“也许该换一个 query”。search 真跑过一次，它才知道这个 query 返回什么。

课件里的 market cap 例子很直观。第一次 search 得到 `nothing found`，Agent 改为逐家公司查；下一次只拿到 stock price，它又发现还缺 outstanding shares。plan 跟着 Observation 变了。

Observation 当然也可能过时、字段错误，网页里甚至会混入 adversarial content。ReAct 把 external feedback 带进 loop，也把新的 failure source 一起带了进来。

## 和普通 Tool Calling 的距离

Tool calling 描述的是 interface。模型输出 function name 和 arguments，controller 执行，再把 result 写回 context。

ReAct 关心的是多轮 trajectory，plan 会不会因为新 Observation 调整。现代 function calling 足够承载这套 loop，没必要继续解析 `Action: search[...]` 这样的文本格式。typed schema 和 tool registry 更好校验。

一次 Tool call 后直接 answer，只能说明系统用过 Tool。它没有展示后续 decision 是否真的依赖 Environment。

## 几组结果

课件汇总了 PaLM-540B 的结果。

| Method | HotpotQA | FEVER | ALFWorld success rate |
| --- | ---: | ---: | ---: |
| Reason / CoT | 29.4 | 56.3 | N/A |
| Act | 25.7 | 58.9 | 45 |
| ReAct | 35.1 | 64.6 | 71 |

论文还报告，ReAct 在 WebShop 上的 success rate 比此前最佳结果高 10 个百分点。这些数字和 benchmark、base model、prompt 绑得很紧。knowledge-intensive QA 里也没有一个方法一直赢，ReAct 会受 retrieval 质量影响，CoT 又可能 hallucinate。

## 落到这周的代码

`experiments/react/react.py` 没有照论文解析 text Action。`Policy` 返回结构化 decision，`ToolRegistry` 校验并执行，controller 把 Observation 写回 history。

我只留了一个 time Tool。正常返回时，下一轮直接用 Observation 回答；faulty scenario 会给一个格式正确、时间错误的结果。这样比再搭一层 framework 更容易看清，Action 带回来的信息究竟怎样进入 answer。

## Sources

- [ReAct paper](https://arxiv.org/abs/2210.03629)
- [Project page](https://react-lm.github.io/)
- [Lecture 02 slides](https://rdi.berkeley.edu/llm-agents/assets/llm_agent_history.pdf)
