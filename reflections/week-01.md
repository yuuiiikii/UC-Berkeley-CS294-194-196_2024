# Week 01 reflection

## 我以前怎么理解 LLM reasoning

Chain-of-Thought、RAG、tool calling 和 multi-agent workflow 都用过，所以 reasoning 对我并不陌生。我习惯把它放进 pipeline 里，模型读 context、拆步骤，再给 answer 或 action。

有个默认假设以前没认真查过。intermediate steps 多一点，再放一个 reviewer，系统应该会更可靠。实际项目里 reviewer 重复原判断时，我通常先去改 prompt。

## 这一周改了什么

reasoning 和 verification 得分开看。CoT 能帮助模型处理 serial dependencies，Self-Consistency 能压掉一部分 sampling noise，但两者都不自动提供 ground truth。

reviewer 没拿到新 information 时，写出的 critique 可能很完整，原来的 blind spot 还在那里。prompt 继续加长，解决不了这个问题。

## 这和 Agent 有什么关系

`Thought -> Action -> Observation` 里，真正可能改变下一轮判断的是 Observation。retrieved evidence、tool result、unit test 或 environment state 带回了什么，比 Thought 写了多少更值得看。

第二周读 ReAct 时，我会继续盯着 Action 后面的变化。context 里没有新增任何东西，那一轮大概率只是又生成了一次。
