# Week 03: Agent frameworks

内部 research assistant 最早就是一串函数调用。query rewriting 之后做 retrieval、reranking，最后把 context 交给 answer generation。后来又加了 planner、executor、reviewer 和 conversation state，流程开始变得难管。

有些 state 没有明确的 owner。某个 agent 已经拿到的结果，另一个 agent 又重新查了一遍。失败时也不总能看出来是谁决定继续、谁决定结束。最后只能不断补日志和条件分支。代码能跑，control flow 还是越来越难读。

## Framework 到底解决什么

发一次 LLM request 并不难。麻烦通常出在 request 外面。消息交给哪个 role，tool result 写回哪里，这一轮结束后继续还是停，都要有地方处理。

第二周的 loop 很短。

```text
LLM -> Thought -> Action -> Observation -> LLM
```

当系统里出现多个 Agent，问题很快变成了另一种形式。

```text
Agent A -> Agent B -> Tool -> Agent C -> Agent A
```

Agent 多起来以后，每个 role 都带着自己的 context，消息还要在它们之间来回传。谁发的、谁收的、tool 有没有报错、这一轮为什么结束，这些记录很快就散进 callback 和 prompt 里。Framework 至少给了它们一个固定的位置。

当时最难调的就是 control plane。模型给出下一步之后，系统还得检查这一步能不能执行，再把消息和结果送到正确的位置。直接拿一段自然语言去控制流程，出错时很难追。

## AutoGen 和 LlamaIndex 放在一起看

AutoGen 这部分讲的是 conversable agents。Agent 通过统一接口收发消息，auto-reply 让 conversation 往下走。有的 role 接 LLM，有的接 human input，也可以把 tool 或 code execution 挂进去。

LlamaIndex 那节课离我做过的 RAG 链路更近，data connector、retrieval 和 context 组织都很熟悉。可一旦 assistant 能继续查、换 query 或调用别的 tool，原来固定的 pipeline 就不够用了。current state 放在哪里，也得重新想。

这两段内容的落点不太一样。AutoGen 花更多篇幅处理 conversation 和 multi-agent orchestration。LlamaIndex 贴着 data 与 knowledge workflow 往上搭，一个实际项目完全可能两边都用到。

## Agent 越多越好吗

Agent 一多，context 先变得麻烦。每次 handoff 都可能丢信息，还会多一次 model call。角色拆开当然也有好处，不同 prompt 可以单独测，code execution 和 human approval 也不必塞进同一个 role。

retrieve、rerank、answer 本来就是固定顺序。硬拆成三个 conversation，quality 未必会动，latency 和 trace 倒是马上变长。reviewer 如果读的还是同一份错误 context，也很难算独立检查。

我在项目里真正缺过的是某一步的独立检查，或者只有特定 role 才能用的 tool。单纯再起一个相同 model、喂同一份 context，通常只会多出一段 conversation。

## 谁决定下一步

AutoGen 的 auto-reply 可以直接把 conversation 推下去，Python 代码仍然能限制最大轮数和 termination。到了 dynamic group chat，`GroupChatManager` 还会选下一位 speaker，这个选择也可以交给 LLM。

speaker 交给 LLM 之后，trace 里就得看它为什么把任务转给某个 role，还得防止两个 role 来回转发。analyst 后面固定接 checker 的流程没这个必要，直接写在 controller 里更省事。

StateFlow 把这个问题往前推了一步。它把整个 task-solving process 写成 state machine，让 state transition 和 state 内的 sub-task solving 分开。这样模型仍然可以在某个 state 内生成内容或调用工具，但它不需要每一轮都重新发明整个流程。

## 放回一个小系统

小系统里的 controller 直接写在 Python 里。Agent 只处理交给自己的那一步。

```text
controller
    -> analyst(task, context)
    -> checker(analysis, evidence)
    -> answerer(checked result)
```

每一步只拿到它需要的输入，controller 记录 state、调用次数和结束原因。dynamic branch 暂时没加，当前任务用固定顺序就能跑完。

小实验里的 analyst 先算 cache latency，checker 再检查公式，answerer 只负责整理答案。多出来的两次 mock call 到底做了什么，跑完就能直接看到。

## Sources

- [Course website](https://rdi.berkeley.edu/llm-agents/f24)
- [AutoGen lecture slides](https://rdi.berkeley.edu/llm-agents-mooc/slides/autogen.pdf)
- [LlamaIndex multimodal knowledge assistant slides](https://rdi.berkeley.edu/llm-agents-mooc/slides/MKA.pdf)
