# Paper notes: AutoGen

## AutoGen 解决的麻烦

planner 把任务交给 executor，executor 再把结果交给 reviewer，失败时回到 planner。这样的 multi-agent workflow 用几个 role 加几段 glue code 就能写出来。角色本身不难，消息、context 和 termination 很快会散落在各处。

AutoGen 把这些 role 做成可以收发消息的 conversable entity。每个 Agent 有自己的 context，背后可以接 LLM、human input 或 tool。这样写比“一个 Agent 对应一段 prompt”更接近真正跑起来的系统。

## 为什么要多个 Agent

论文里的 AssistantAgent 通常负责生成方案。UserProxyAgent 接 human input，也能执行 code 或 function call。它们之间的内容走 message，调试时至少能看到某个结果是谁发出来的。

planner、executor 和 reviewer 要是都用同一个 model，还读着同一份错误 context，很可能只是把一份判断传了三遍。角色名不会让 reviewer 自动独立。它得拿到别的 evidence，或者真的能执行 verifier、unit test、human approval 之类的检查。

## Agent 之间怎样交流

论文里的 Agent 有统一的 send、receive 和 generate_reply 接口。一个 Agent 收到消息后，可以根据自己的配置生成回复，再把回复发回去。默认的 auto-reply 机制会让对话继续，直到满足 termination condition。

读代码时我会把它当成事件循环。message 到达 Agent，`generate_reply` 处理完又发出一条新 message。两个 Agent 来回聊很好理解，role 再多一些，重复回复和停不下来的情况就得单独处理。

完整 transcript 一路往后传，context 很快就会膨胀。我之前更习惯给 checker 单独准备输入，把 task、evidence 和当前 answer 放进去，再告诉它能做哪些检查。它不需要重新读完整段聊天。

## 谁决定下一步

简单的两个 Agent 对话里，收到消息的 Agent 可以直接 auto-reply。更复杂时，应用代码可以注册 reply function，或者用 function call 让 LLM 决定要不要找另一个 Agent。

论文还讨论了 dynamic group chat。`GroupChatManager` 可以根据当前对话选择下一个 speaker，再把回复广播给其他 Agent。这个设计比固定的 A、B、A 顺序灵活，但 speaker selection 本身也成了新的 failure point。它可能选错人，也可能让两个角色互相转发，直到 budget 用完。

dynamic group chat 需要 manager 选 speaker，这对开放任务有用。不过 analyst 做完就交给 checker 的流程，没必要再请求一次 LLM 来选人。这一步直接写进 Python controller 就够了。

## Multi-Agent 什么时候值得用

code execution 是比较容易说明的场景。负责写方案的 Agent 不一定应该拥有执行权限，交给 UserProxyAgent 或单独的 executor 会清楚很多。human approval 也类似，它本来就来自系统外部。

reviewer 真能运行 unit test，或者重新查一个 source，拆出来也说得通。它拿到了前一个 role 没有的 evidence。任务可以并行时，多 role 还可能省时间。已经稳定的单 Agent 再包一层 message passing，通常只会多出 token 和 latency。多采样带来的提升也容易被算到 multi-agent 头上，这一点得分开看。

## 放回之前的 workflow

之前那个 prototype 里的 planner、executor、reviewer 更像几个函数。消息能传过去，但输入里该有哪些 context、输出是什么 schema，并没有认真定过。于是 planner 偶尔顺手调 tool，reviewer 也会在没有新 evidence 时重写 answer。

这次 demo 干脆固定成 analyst -> checker -> answerer，speaker selection 暂时用不上。dynamic routing 留到固定顺序真的卡住时再说。

## 我还没完全想明白

生产系统里，conversation 和业务 state 怎么同步，我还没想明白。一个 Agent 修改了外部 environment 之后，其他 Agent 看到的到底是原始 message、压缩 summary，还是重新读取后的 state？AutoGen 的 conversational abstraction 很适合快速组装实验，这部分边界却还需要继续看。

这和第一周的 self-correction 也接得上。多个 Agent 只有在获得不同 evidence 或不同约束时，才更像独立的 check。角色名字本身不会制造 independence。

## Source

- [AutoGen paper](https://arxiv.org/abs/2308.08155)
- [AutoGen lecture slides](https://rdi.berkeley.edu/llm-agents-mooc/slides/autogen.pdf)
