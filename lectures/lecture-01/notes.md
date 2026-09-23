# Week 01: LLM reasoning

之前做 internal research assistant，问题大多出在 retrieval、prompt 和 context packing。搜不到 evidence，模型就开始补；context 太长，最相关的段落反而没被用上。久而久之，我很容易把错误都归到输入上。

这节课补了一种更麻烦的情况。evidence 没问题，模型仍然会在多步 reasoning 里走错，而且写出来的过程可以很顺。

## 一段 reasoning trace 能说明什么

老师开头问，LLM 说自己“想明白了”，这能算证据吗？

模型生成了一串有顺序、有因果关系的文字。对 serial task 来说，这些 intermediate steps 有时确实能保存中间结果，让后一步接着算。可我们看到的还是 output，不是经过检查的 proof。

RAG 里的 citation 也有类似问题。answer 带了 citation，不等于 claim 真被那段 evidence 支持；CoT 写得完整，也不等于每一步都成立。

## CoT 用起来有效，但它不负责验算

我在 prompt 里用过 Chain-of-Thought。让模型先展开 intermediate steps，通常比直接要 final answer 稳一些，尤其是步骤互相依赖的时候。debug 也方便，至少能看到错误从哪里开始。

麻烦是第一步一旦算错，后面完全可以顺着错的结果继续写。模型原来答对了，被要求“检查并解释”后又改错，也不奇怪。CoT 给了 computation 更多空间，没有顺便送来 ground truth。

只看 final answer 会混进猜对的样本；只看 trace 也不够，一段 explanation 可能是事后补出来的。真要评估，还是得回到具体步骤用了哪些 premise，前后能不能接上，最后的 conclusion 是否真的由前面推出。

## Self-Consistency

Self-Consistency 会对同一道题采样多条 reasoning path，再给 final answer 投票。我以前把它简单理解成“多问几次，取多数”。这次更在意的是 paths 有没有真的分开。

采样有 diversity 时，投票能压掉一部分随机错误。大家共享同一个误解，多数票只会很有把握地一起错。它还会直接增加 token 和 latency，却没有像 calculator、code test 或 database query 那样带回新 evidence。

## reviewer 为什么可能没用

planner、executor、reviewer 这几个 role 我都搭过。reviewer 看起来像多了一层保障，可三个 role 如果共享 model 和 context，错误也会共享。reviewer 有时只是把原判断换种说法，还有可能为了完成“找问题”的任务，把正确 answer 改坏。

真正能让下一轮发生变化的，往往是 `Observation`。

```text
reason -> act -> observe -> update state -> reason again
```

calculator result、retrieved evidence、unit test 和 environment state 都可能带回模型之前不知道的东西。当然，tool result 也会错，但至少问题变成了可以追踪的 external signal，而不只是再反思一轮。

## 还没想清楚的地方

LLM 到底是在执行 learned algorithm，还是复用了训练数据里的 pattern，我现在分不清，实际表现大概也混着两者。

任务差异也很大。code task 有 unit test，arithmetic 可以交给 calculator，开放域问答却经常找不到同样干净的 verifier。第一周我没有硬写 benchmark，能把 reasoning 和 verification 分开已经够用了。

## Sources

- [Course website (Fall 2024)](https://rdi.berkeley.edu/llm-agents/f24)
- [Lecture 01 slides: LLM reasoning](https://rdi.berkeley.edu/llm-agents/assets/llm-reasoning.pdf)
