# Week 04: Enterprise generative AI and agents

internal research assistant 收到 question 后，会先做 query rewriting，再走 hybrid retrieval 和 reranking。answer generator 拿到的已经是整理过的 context。当时出了错，我大部分时间都在看 retrieval score，citation 只要能指回某个 chunk，通常就算过了。Week 4 讲 Grounding，刚好补了这一段。

## Grounding 比 RAG 稍微宽一点

Google 的材料里，grounding source 可以是内部文档、Search、database，也可以是一条 tool result。RAG 负责取回材料，generation 还要受这些材料约束。

citation 这一步曾经让我误判过。retrieved chunk 和问题谈的是同一件事，答案里的数字却来自 model prior，末尾那条 source link 仍然看起来很正常。prototype 里已经有 retrieval trace，但没有细到能看出每个 claim 用了哪句 evidence。

把当时的链路重新写一遍，大概是这样。

```text
question
   -> query / filter
   -> retrieval
   -> reranking
   -> context packing
   -> generation
   -> answer + citation
```

query 没带上业务里的说法，后面就查不到。旧制度和新制度高度相似，semantic score 很难拉开。正确 chunk 进了 context 也还没结束，model 有时会抓住旁边那个更像答案的句子。

## Long context 里仍然会漏

Needle in a Haystack 直接把答案放进 context，然后改变 context length 和 needle depth。GPT-4 测到 128K，Claude 2.1 测到 200K，漏检仍然出现，而且位置会影响结果。

我之前有个省事的做法。retrieval 不太稳，就多塞一些 chunks。recall 的确会好看一些，有用的两段也要跟着挤进更多干扰内容。过去碰到回答出错，我很容易继续调 top-k 或 reranker，很少单独检查 model 有没有用上已经取回的句子。

long context 留完整段落很方便，跨文档关系也不容易被 chunk boundary 切断。最大窗口现在对我更像一个 hard limit，实际放多少仍然看 task eval。

## 版本、权限和 eval

第四周 demo 同时放了 2024 和 2026 两版差旅制度，北京住宿上限分别是 550 元和 650 元。只做 similarity search，它们本来就应该很接近。我给 archived document 降了权，真实系统还会碰到生效地区、员工类型和例外条款。

权限得更早处理。retrieval layer 一旦把无权查看的内容送进 context，generation 阶段再删掉原文已经晚了。ACL filter 要跟着 user identity 进入查询，不能只写在 system prompt 里。

demo 的 results table 把 retrieval hit 和 answer correctness 分开记。成都住宿那条因此没有被藏掉。正确 source 已经在 top-3，final answer 仍然错了。接入 LLM 以后还得再加 citation faithfulness。

## Agent 在这里多做了什么

固定 RAG 收到问题后检索一次。Agent 把 retrieval 当作 Action，看到 Observation 不够，还能 rewrite query 或换 source。调查式任务会用到这种 loop。

它也会把一次错误 retrieval 带进下一轮。planner 围着错误 evidence 继续搜索，trace 会越来越长，答案甚至可能显得更完整。source policy、budget 和 stop condition 还是由代码管更踏实。

demo 暂时没接 LLM，先把 ingestion、ranking、abstention 和 citation 跑通。12 条问题里有一条完全没找对 section，还有一条已经取回正确 section，answerer 却挑错了句子。什么时候重查、什么时候停，我还没有一套满意的规则。

## Sources

- [Course website](https://rdi.berkeley.edu/llm-agents/f24)
- [Enterprise Generative AI lecture slides](https://rdi.berkeley.edu/llm-agents-mooc/slides/Burak_slides.pdf)
- [Google Cloud: RAG and grounding on Vertex AI](https://cloud.google.com/blog/products/ai-machine-learning/rag-and-grounding-on-vertex-ai)
- [The Needle in a Haystack Test](https://towardsdatascience.com/the-needle-in-a-haystack-test-a94974c1ad38)
