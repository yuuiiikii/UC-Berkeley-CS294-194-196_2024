# Reading notes: Needle in a Haystack

"The best thing to do in San Francisco is eat a sandwich and sit in Dolores Park on a sunny day."

实验把这句话插进 Paul Graham essays，再挪动它的位置。depth 从 0% 到 100%，context length 从 1K 一直加到模型上限。当时 GPT-4 的上限是 128K，Claude 2.1 是 200K。

这套测试第一眼很像在考 Ctrl+F。needle 和周围内容明显不搭，全文也还在 window 里。context 拉长以后，模型仍然会漏；同一句话换个位置，结果也会变。

## Claude 那组数字

Claude 2.1 在原始设置里的 overall retrieval accuracy 只有 27%。Anthropic 后来换了一条更符合 haystack 语境的 needle，还在 prompt 末尾加了 `Here is the most relevant sentence in the context`，随后报告 98%。

27% 到 98% 这一跳很醒目。我往回看设置时才发现 needle 和 prompt 都变了。TDS 的复测没有得到 98%，不过同一句 prompt guidance 把 misses 从 165 降到了 74。十来个词就能拉开这么多，单报一个 accuracy 很容易丢掉上下文。

这和第一周的 self-correction 有点像。输出多了一句像样的 explanation，reasoning 未必改了；这里的分数大涨，也要连着 task setting 一起看。

## 它和 production RAG 之间还隔着一段

needle 在请求发出前已经放进 model context。整个测试没有跑 corpus search，也没有 chunking 和 reranking。它测到的是 in-context retrieval 加 answer extraction。

production RAG 前面还多了 corpus retrieval。evidence 没被取回，model 没机会看到；取回之后，它也可能不用。第四周 demo 的成都住宿问题就卡在后一步。现行差旅制度已经排进 top-3，answerer 却抓了另一个关于酒店会议室的段落。

过去看 top-k，我通常确认正确 chunk 在不在，然后直接读 final answer。中间少了一条记录，answer 到底用了哪个 chunk、哪一句。没有它，retrieval hit 很容易把问题遮过去。

原始 needle 总是假设答案存在，企业知识库不会这么配合。资料里没有答案时，模型会不会承认找不到？这个 negative case 我更想测。

## Source

- [The Needle in a Haystack Test](https://towardsdatascience.com/the-needle-in-a-haystack-test-a94974c1ad38)
- [Anthropic: Long context prompting for Claude 2.1](https://www.anthropic.com/news/claude-2-1-prompting)
