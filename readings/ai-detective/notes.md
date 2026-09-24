# Reading notes: AI Detective

这篇本来就是 product article，能记下来的 method 不多。材料被放进一份 case context，model 从中找线索，再把散在不同位置的信息接起来。一次回答可能同时依赖几处 evidence，单条 needle 已经不太够描述这种任务。

整份材料交给 long-context model，段落不会先被切碎，跨章节的关系也还留着。每轮都传一大段 context，latency 和 cost 会涨。source 更新后得重新组装，权限不同的用户也不能共享同一份 context。

internal knowledge base 会不断加文档，全文塞入迟早走不下去。之前的项目会先用 metadata filter 排掉过期或无权访问的 source，再做 retrieval，剩下的材料多保留一点上下文。

detective-style task 还有个麻烦。答案错了，很难马上分清是漏了 clue，还是 model 把两个 clue 接错了。只存 final response 不够，送进 model 的材料和实际 citation 都得留在 trace 里。

第一批 evidence 不够时，谁来触发下一次 search，我还没定下来。这次 demo 没做 retry。controller 里写固定次数比较好追踪，开放任务又很容易把规则写死。无论用哪种，每轮新加入的 evidence 都得单独留在 trace 里。

## Source

- [Google Cloud: The Needle in the Haystack Test and how Gemini Pro solves it](https://cloud.google.com/blog/products/ai-machine-learning/the-needle-in-the-haystack-test-and-how-gemini-pro-solves-it)
