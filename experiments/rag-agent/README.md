# Local policy RAG

这个 demo 用的是几份虚构公司制度。现行差旅政策把北京住宿上限写成 650 元，归档版本里是 550 元，两份文档都会进入 index。这样比只放一条干净答案更容易看到 ranking 出错。

代码只依赖 Python standard library。`ingest.py` 按 Markdown section 切块，`retrieve.py` 做 BM25-style sparse retrieval，`agent.py` 从取回的内容里选一句 evidence，并把 `source#section` 放到答案末尾。

```text
Markdown policies
      -> section chunks
      -> sparse retrieval
      -> evidence sentence
      -> answer + citation
```

这里先没接 embedding、reranker 和 LLM generation。小语料用 term overlap 就能跑，也方便打开 score 看问题出在哪。这个版本留下了两个失败样例，结果记在 [results.md](results.md)。

## Run

```bash
python3 experiments/rag-agent/ingest.py
```

```bash
python3 experiments/rag-agent/retrieve.py "出差住宿一天最多报销多少？"
```

```bash
python3 experiments/rag-agent/agent.py \
  --question "北京出差住酒店，每晚最多能报销多少？"
```

```bash
python3 experiments/rag-agent/agent.py --eval
```

`Direct` 看不到内部文档，只能拒绝确认公司规定。`RAG` 读取 top-3 chunks，score 太低时会 abstain。12 条 evaluation questions 里有 paraphrase、旧版政策、干扰文档和一个语料中不存在的问题。

## Files

- `data/` 是 policy corpus，front matter 里有 version、effective date 和 status。
- `ingest.py` 生成本地 `index.json`。
- `retrieve.py` 打印 score、source、section 和版本状态。
- `agent.py` 包含 no-context baseline、grounded answerer 与 12 条 evaluation questions。
