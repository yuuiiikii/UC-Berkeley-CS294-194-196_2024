# Week 04 Reflection

12 条问题跑完，RAG 对了 10 条。成都住宿那条最别扭。现行差旅制度已经进了 top-3，answerer 拿走的却是采购制度里关于酒店会议室的句子。retrieval metric 算 hit，用户看到的答案还是错的。

之前调 hybrid retrieval，我花在 top-k、score、query rewriting 上的时间很多。正确 source 被召回以后，后面似乎交给更强的 model 就行。Needle 里的结果说明这一步没那么省心，context 的长度、位置和 prompt 都会影响 model 最后用了哪句话。

旧制度也是这周补上的一个缺口。demo 同时存了 2024 年的 550 元和现行的 650 元，archived status 参与 ranking 后，新版才排在前面。真实的内部文档还有地区、员工类型和 ACL，光靠 embedding score 肯定不够。

Agent 在 evidence 不足时可以重新搜索，麻烦在 stop condition。健身补贴那条根本没有 source，继续 rewrite 很可能只会捞到越来越远的段落。当前 demo 直接 abstain，至少没有编数字。

citation faithfulness 这次还测不到。extractive answerer 原样拿一句话，引用自然能对上；接入生成式回答以后，一句话可能混入三段材料和 model prior。下次可以专门放几条互相冲突的政策，看每个 claim 最后落到哪里。
