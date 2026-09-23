# Week 02: LLM agents, history and overview

实习时做过一条 research assistant 链路，里面有 query rewriting、retrieval、reranking、tool routing，也试过 planner、executor 和 reviewer。大家一直把它叫 Agent，我也跟着叫，没有细究哪些路径其实早就写死了。

第二周正好碰到这个边界。LLM、Tool 和 Environment 都出现了，还不一定有一个真正跑起来的 Agent loop。

## 一次 Tool call 还不够

下面这条线看起来像不断加组件。

```text
LLM
  -> LLM + Tool
  -> LLM + Tool + Environment
  -> Agent
```

单独的 LLM 读 context 后生成内容。接上 Tool，模型可以请求 search、calculator 或 code execution。Environment 暴露外部 state，Action 执行后，下一轮看到的内容可能已经变了。

controller 把这些东西接成 loop。

```text
Goal
  -> observe current state
  -> choose an action
  -> execute it in the environment
  -> read the new observation
  -> update state and continue or stop
```

一次 function call 也可能只是固定 workflow 里的一个节点。tool result 写回 context，模型根据新 state 改变下一步，trajectory 才真的开始分叉。这里讨论的 Agent 更接近整个 system，不能只看 model 会不会输出 function call。

## Agent 比 LLM 早得多

课件把相关工作分成 text agent、LLM agent 和 reasoning agent。ELIZA、LSTM-DQN 属于 text agent；SayCan 和 Language Planner 用 LLM 选择 Action；ReAct 再把 verbal reasoning 放到行动之间。

Agent 当然早于 LLM。Symbolic AI agent 靠人工规则，RL agent 从 reward 和 interaction 里学 policy。LLM 让 open-ended language 进入 state、instruction 和 plan，很多 prior knowledge 也来自 pretraining。

换到可执行层，老问题还在。Action 合不合法，Observation 能不能信，什么时候该停，模型不会自动替系统处理干净。

## Tool calling 解决的是接口

“这个 Agent 会调用搜索”只描述了 action space。模型选 function name 和 arguments，程序执行后立即结束，这仍然可以是一条 deterministic workflow。

loop 长也不代表质量高。control flow 能提前写清时，普通 workflow 更容易测试，权限也好收。真正难枚举的下一步，需要等 Observation 回来再决定，这时 Agent loop 才有实际作用。

## Environment 不只是网页

网页、文件系统、code executor、database，甚至用户，都可以是 Environment。它决定 Agent 当前能看到什么、允许做什么，Action 又会怎样改变 state。

WebShop 里的模型不能只说“我会搜索商品并选择尺寸”。它得真的提交 search、打开 item、选择 option，再执行 buy。一步点错，后续页面也会跟着变化。

memory 的位置还有点模糊。model context 里的 scratchpad 更像 short-term state；独立 vector store 需要显式 read/write，行为上又很像 Environment。后面讲 Memory 时再回来改这个划分。

## 放回之前的 research assistant

那条链路里，很多路径其实是 deterministic workflow。retrieval result 出来后只能进 answer generation，模型没有机会换 query 或换 Tool。

允许模型根据结果继续查、改 query 或结束之后，trajectory 才分叉。evaluation 也不能只测 recall、rerank quality 和 citation correctness，还得看重复调用、越权、错误 Observation 以及 termination。

`Thought -> Action -> Observation` 写起来很短。ReAct 真正有用的部分，应该都藏在 Action 之后发生的变化里。

## Sources

- [Course website (Fall 2024)](https://rdi.berkeley.edu/llm-agents/f24)
- [Lecture 02 slides](https://rdi.berkeley.edu/llm-agents/assets/llm_agent_history.pdf)
