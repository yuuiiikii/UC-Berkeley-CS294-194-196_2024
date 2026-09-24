# Results

```text
Direct accuracy: 1/12
RAG accuracy: 10/12
Retrieval success: 11/12
```

| # | Question | Direct | RAG | Retrieval |
| -: | --- | :---: | :---: | :---: |
| 1 | 北京出差住酒店，每晚最多能报销多少？ | fail | pass | hit |
| 2 | 去成都出差，住宿标准是多少？ | fail | fail | hit |
| 3 | 一天的出差餐补是多少？ | fail | pass | hit |
| 4 | 酒店超标需要谁批准？ | fail | pass | hit |
| 5 | 年假最多能结转几天，什么时候过期？ | fail | pass | hit |
| 6 | 连续请三天病假要交什么？ | fail | pass | hit |
| 7 | production deployment 需要什么审批？ | fail | pass | hit |
| 8 | SEV-1 事故多久更新一次？ | fail | pass | hit |
| 9 | 6 万元采购要准备几家报价？ | fail | pass | hit |
| 10 | 供应商要访问客户数据，签约前要做什么？ | fail | pass | hit |
| 11 | 半夜起飞能不能坐前舱？ | fail | fail | miss |
| 12 | 公司每月健身补贴多少？ | pass | pass | hit |

北京住宿那条同时召回了两版差旅政策。现行版排第一，回答用了 650 元；归档版的 550 元仍在 top-3。status 降权这次起作用了，不过旧数字依然会进入 context。

成都住宿这条更麻烦。现行差旅制度在 top-3 里，排第一的却是采购制度中的酒店会议室。answerer 最后也选了这一段。retrieval hit 因为 top-3 包含正确 source 而通过，final answer 没通过。

“半夜起飞能不能坐前舱”直接 miss。文档里写的是 `overnight flight` 和“经济舱”，当前 query expansion 没有处理这组表达。score 没过阈值，answerer 返回 abstain。换大 generator 也看不到那段制度，这条要从 query rewriting 或 embedding retrieval 下手。

健身补贴在 corpus 里不存在。retriever 还是给了几条低分结果，abstention threshold 没让 answerer 用这些段落拼数字。no-context baseline 只在这一题算对，所以最后是 `1/12`。
