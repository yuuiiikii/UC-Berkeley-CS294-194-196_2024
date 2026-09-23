# Paper notes: StateFlow

## ReAct loop 里的状态问题

第二周的 ReAct loop 把下一步交给模型决定。这样很灵活，模型也要在每一轮重新判断自己现在处于什么阶段、还缺什么信息、该不该结束。任务稍微长一点，状态判断本身就会成为风险。

StateFlow 把 task-solving process 表达成 state machine。每个 state 表示当前流程状态，进入 state 后执行一组 actions，再根据 context 和执行结果决定下一个 state。这种写法和我以前做过的 workflow 很接近。

进入某个 state 后，LLM 或 tool 只处理当前 sub-task。做完以后再走 transition，代码和规则可以参与决定下一个 state。模型不用每一轮都从完整 history 里猜流程走到哪了。

## 为什么不用一个 prompt 说清楚流程

ReAct 经常把任务说明、示例轨迹、历史 observation 和下一步选择放在一个循环里。它能跑起来，但模型要自己维护当前阶段。论文的说法比较直接，不能一直假设 LLM 会正确判断 progress 和下一步 trajectory。

一个 RAG pipeline 如果把 query rewrite、retrieve、rerank、answer 和 citation check 全放进 agent prompt，demo 可能很顺，失败时却很难确定是哪一段出了问题。显式 state 会让日志和评估落到具体阶段，这和我之前碰到的情况很接近。

## StateFlow 怎么组织流程

流程大致长这样。

```text
current state
    -> state-specific instruction
    -> LLM or tool actions
    -> observation in context
    -> transition rule
    -> next state
```

每个 state 可以有自己的 prompt 和 actions。transition 既能写 heuristic，也能让 LLM 判断。autonomy 还在，只是“现在走到哪一步”不再完全藏在 prompt 里。

论文里的 SQL case 用了 Init、Observe、Solve、Verify 和 Error 等状态。成功执行 `SHOW TABLES`、`DESC` 或 `SELECT`，以及遇到错误字符串时，transition 会不同。这个例子对我很有帮助，因为它把一个模糊的“继续想”改成了几个可以检查的分支。

Error state 也值得留意。很多 agent workflow 只描述成功路径，出错后让模型自己想办法。StateFlow 把 error handling 写进流程，至少可以看出错误发生后允许哪些 actions，以及什么时候重新回到 Solve。

## 论文结果应该怎么读

论文报告 StateFlow 在 InterCode SQL 和 ALFWorld 上相对 ReAct 分别提高 13% 和 28% 的 success rate，同时成本降低约 5 倍和 3 倍。这个结果和 benchmark、prompt、model 以及 workflow 设计绑定得很紧。它最多能说明显式流程在这两个设置里同时改善了效率和可控性，推不到所有 Agent 都应该使用 state machine。

移除 Observe、Verify 或 Error 后，表现会受到影响，具体幅度又和任务有关。state 的价值来自它对应了一个真实的 decision point，堆几个名字不会自动改善 system。

## 它和 AutoGen 的关系

AutoGen 论文花了很多篇幅讲 Agent 怎么互发消息。StateFlow 盯着另一件事，任务已经走到哪一步，接下来允许转到哪里。读起来不像在抢同一个 abstraction。

把 AutoGen Agent 放进每个 state，在代码上没有问题。只是 conversation 和 state transition 会同时出现，trace 马上多一层。当前 demo 先把 state 跑通，没有再叠 role conversation。

## 放进自己的 workflow

拿第二周的 ReAct demo 来改，最直接的是把 tool error 单独接到一个 state，而不是继续把错误文本丢回同一个 prompt。拿到可用结果后再进 verification，失败就回到 action。原来已有的 max tool calls 和 max steps 继续由 controller 管。

trace 也要多记一项，Agent 什么时候进入或离开某个 state。只有 Thought、Action、Observation 的话，还是不容易看出流程为什么拐到另一条路径。

## 还留下的问题

state 的粒度最难拿。tool 报错这种明确事件很适合做 transition；模型措辞稍微变了一点，没必要再拆一个 state。切得太碎以后，controller 会被条件分支塞满。我还没有通用的标准。

至少在这个 demo 里，Agent 可以自己决定 state 内怎么分析。流程往哪里走，还是留给能测试的 transition。这里少一点 autonomy 没什么问题。

## Source

- [StateFlow paper](https://arxiv.org/abs/2403.11322)
- [Course website](https://rdi.berkeley.edu/llm-agents/f24)
