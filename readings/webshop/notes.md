# Paper notes: WebShop

WebShop 让 Agent 去“购买”商品。换成“推荐”以后，任务立刻轻了很多，模型写一句像样的答案就行。purchase 要求它真的在 Environment 里走到最后一步。

## 页面会跟着 Action 变化

instruction 里可能有产品类型、attribute、option 和价格。Agent 要提交 search，打开详情页，比较信息，选 size 或 color，最后 purchase。action space 由 search query 和页面上的 text button 组成。

每一步都会拿到新的 Observation。episode 结束后，Environment 根据商品类型、attribute、option 和价格算 reward。

论文使用 1.18 million 个 real-world products、12,087 条 crowdsourced instructions 和 1,600 多条 human demonstrations。Environment 有 HTML mode，也有删去部分网页 metadata 的 simple mode，后者供模型使用。

## 合法 Action 也会走错

一句“我建议购买红色防水外套”在这里没有用，系统最后检查的是 product 和 option。

search query 可能漏掉 attribute；标题看着合适，详情页却不满足要求；商品选对了，size 又错了。前面点进错误页面，后面的 visible state 也会一起变化。

论文分析 human trajectory 时提到 impatience。有些参与者搜一次就购买当前商品，expert 更愿意返回并 refine search。这个现象很像 browser agent 的失败录像。每个 Action 都合法，只是太早决定任务已经完成。

## 29% success rate

论文里的 best model success rate 是 29%，rule-based heuristic 是 9.6%，human expert 约 59%。Task Score 允许 partial credit，Success Rate 只统计完全满足要求的 episode。

reward design 对数字影响很大。大部分 attribute 匹配可以拿到不错的 partial score，漏掉 required option 仍然算失败。真实 purchase 更严格，一次错误 Action 可能真的花钱。

## 它和固定 RAG 不太一样

我做过的 RAG 通常返回一组 documents，generator 在固定 context 上回答。WebShop 里的 search 会改变 trajectory。Agent 先写 query，读 result page，再决定打开哪个 item，必要时返回重搜。

retrieval quality 只是其中一段。Agent 还得记住 instruction，在 noisy page text 里追踪 current state，最后别太早按下 buy。

真实网站会再多出 purchase confirmation、预算、库存变化、prompt injection 和不可逆 Action 的审批。WebShop 的 automatic reward 依赖 attribute matching，也不等于人类判断。benchmark score 高，离安全操作真实电商还有很远。

这周没有复现整套 WebShop。光把 Environment 跑起来就会占掉不少时间，而 ReAct time-agent 已经足够让我观察 Action 和 Observation 的关系。

## Sources

- [WebShop paper](https://arxiv.org/abs/2207.01206)
- [WebShop project](https://webshop-pnlp.github.io/)
- [WebShop repository](https://github.com/princeton-nlp/WebShop)
