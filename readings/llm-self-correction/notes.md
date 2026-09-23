# Paper notes: Large Language Models Cannot Self-Correct Reasoning Yet

之前的 Agent prototype 里有一个 reviewer。answerer 生成答案后，它检查 citation、遗漏和逻辑问题。明显错误偶尔能抓到，副作用也很明显。原答案已经有 evidence 时，reviewer 仍会写一句“这里可能不够严谨”，接着把内容改得更模糊。

当时我继续给 reviewer prompt 加 instructions。可 prompt 不是唯一的问题，reviewer 手里根本没有新 information。

## 没有 external feedback 的 correction

论文讨论的是 *intrinsic self-correction*。模型拿回自己的回答，做 critique 和 revision，中间没有 standard answer、tool result 或明确的 error signal。

这和 code agent 跑 unit test 不一样。calculator、retriever 或 human feedback 会往 loop 里放进一个 external signal；intrinsic self-correction 主要靠模型重新读自己写过的内容。

论文在 GSM8K、CommonSenseQA 和 HotpotQA 等任务上分别看 error detection、critique 和 revision。这里很容易把几件事混在一起。模型知道“原答案错了”之后能不能修，和它能不能自己发现错误，测的并不是同一件事。多给一轮 inference budget，也应该和同预算的 multiple sampling 或 Self-Consistency 比。

## 我记住的数字

论文抽样的 200 道 GSM8K 题里，GPT-4 初答准确率是 95.5%。没有 external feedback，修改一轮后降到 91.5%，两轮后是 89.0%。这些数字属于论文当时的 model、prompt 和 task setting，不能直接套到今天的模型上。

其中一个例子更容易记。模型原本正确算出某人 30 天消费 75 元，被要求找出错误后，反而把答案改成 37.5 元。“请检查错误”很可能被理解成“这里一定有错”，review 于是又变成了一次 generation。

## oracle label 容易混进来

有些实验会先告诉模型当前答案是错的，再让它修改。这个 oracle correctness label 已经提供了 signal。实验能说明模型收到“需要修正”后会怎样做，却回答不了它能否独立判断什么时候该改。

放进 Agent pipeline 里，大概是下面这条线。

```text
draft -> reviewer -> revision
```

reviewer 没有 test result、retrieval evidence 或 evaluator signal，只能从语言里猜。换成另一个 role 不会凭空得到 oracle。

## 回到 Agent 设计

`LLM + reflection prompt` 更像 self-critique layer。要叫 verification layer，至少得说清 verifier 比 generator 多知道了什么。

RAG 场景里可以让 answerer 先写 answer，retriever 提供 evidence，verifier 再对 claim 和 evidence。code task 则有 compiler 和 tests。revision 跟着这些具体 signal 走，比一句泛泛的“请认真检查”可靠得多。

multi-agent 也绕不开同一个问题。多个 role 能分工；它们共享错误 context 时，错误同样会沿着 message 传下去。

## 还没确定的边界

arithmetic、code debugging 和开放域问答的情况差得很远。前两类任务比较容易接 executable feedback，开放域问题常常只剩语言判断。

标题里的 `Yet` 不能丢。论文并没有证明 LLM 永远无法 self-correct。它展示的是更窄的限制，在缺少可靠 external feedback 的 reasoning task 里，一段像样的 critique 还不能当作 correction 已经发生。

## Sources

- [Paper: arXiv:2310.01798](https://arxiv.org/html/2310.01798)
- [Lecture 01 slides](https://rdi.berkeley.edu/llm-agents/assets/llm-reasoning.pdf)
