# Week 02 reflection

`Thought -> Action -> Observation` 以前就见过，tool router、RAG 和 reviewer 也都搭过。第二周没有带来一套陌生 framework，变化出在 Agent 的边界上。

## Tool 和 Agent loop

过去看到 LLM、Tools 和多轮调用，我就很容易把整条链路叫 Agent。现在回看，很多路径只是 deterministic workflow。Action 执行后，模型能不能读到新的 state，并据此改变下一步，这个差别更实在。

ReAct 把第一周的 reasoning 问题接到了 external feedback。模型留在 context 里继续想，不会凭空多出 evidence；search result、calculator output 或 Environment state 才会给下一轮 decision 新东西。

## WebShop

WebShop 又多了一层 sequential decision。search、open item、select option 和 buy 都会改变 trajectory。最后检查的是买了什么，不是解释写得顺不顺。

固定 RAG 的 retrieve-then-generate 没有这种分叉。模型能改 query、换 Tool、继续查或停止后，state tracking 和 termination 才真正变成问题。

## faulty tool 比 no tool 更麻烦

time-agent 的 `no-tools` 很干净。Policy 知道没有 current state，直接拒绝猜时间。`one-call` 拿到正确 Observation 后也顺利结束。

`faulty-tool` 返回了格式正常的错误时间，Policy 原样相信。Action 带回 information，不等于 information 可靠。这个 failure 比 tool 报错更难发现。

时间查询风险不高，一个 source 勉强说得过去。purchase、代码修改或 external communication 就不能这么随便，confirmation、cross-check 和 rollback 都要提前放进流程。

## 现在怎么区分

LLM 根据 context 生成 decision。Agent 在外面读 Environment、执行 Action、保存 state、处理错误，再决定继续或停。

control flow 已经写得很清楚的任务，我还是会用普通 workflow。测试和权限都简单。下一步必须等 Observation 回来才知道时，Agent loop 才值得那部分复杂度。
