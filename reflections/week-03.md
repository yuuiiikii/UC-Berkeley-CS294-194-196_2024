# Week 03 Reflection

planner、executor、reviewer 一拆开，每个 prompt 的职责确实清楚了一些。消息怎么传、context 谁持有、什么时候结束，这些麻烦却没有跟着消失。AutoGen 让我重新看了这部分。role 名字可以晚点定，消息和权限乱了以后更难补。

internal research assistant 当时把 query rewriting、hybrid retrieval、reranking、context packing 和 answer generation 串在一个 workflow 里。加上 planner 和 reviewer 后，重复检索、state 过期、失败后重复重试很快都冒了出来。那时主要靠日志和条件分支补洞，没有马上把流程抽成明确的 state machine。现在回头看，流程边界一模糊，连 failure 属于 retrieval、tool execution 还是 transition 都说不清。

`trap` 场景里，checker 找到了漏掉的 lookup cost，答案真的变了。到了 `clear`，它做了同样的修正，最终还是 yes。多出来一个 checker 是否值得，得看它手里到底多了什么。这个 mock 里是另一遍计算；实际项目里也许是 unit test，也许是新的 retrieval result。

放到这种流程里，analyst 可以自己决定怎么算，checker 也可以选择要不要调用 verifier。可用 tool、最大预算和下一步能转到哪里，还是由 controller 管着更踏实。trace 和 retry 都好处理一些。

我还分不太准 multi-agent 和单 Agent 加 state machine 的边界。后面碰到合适的任务，可以各跑一个版本，再看看 dynamic routing 值不值得加。除了最终答案，重复工作和 token 也要记，不然很容易只看到 role 变多了。
