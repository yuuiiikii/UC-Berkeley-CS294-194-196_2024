from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from ingest import DEFAULT_INDEX_PATH, build_index, tokenize


QUERY_ALIASES = {
    "酒店": ["住宿"],
    "每天": ["每日", "每晚"],
    "一天": ["每日", "每晚"],
    "标准": ["上限"],
    "餐补": ["餐费", "补贴"],
    "批准": ["审批"],
    "过期": ["失效"],
    "生产环境": ["production"],
    "事故": ["incident"],
    "供应商": ["vendor"],
    "客户数据": ["customer data"],
    "报价": ["quote"],
}


def expanded_query_tokens(query: str) -> list[str]:
    tokens = tokenize(query)
    lowered = query.lower()
    for phrase, aliases in QUERY_ALIASES.items():
        if phrase in lowered:
            for alias in aliases:
                tokens.extend(tokenize(alias))
    return tokens


def load_index(index_path: Path = DEFAULT_INDEX_PATH) -> dict[str, Any]:
    if not index_path.exists():
        return build_index(index_path=index_path)
    return json.loads(index_path.read_text(encoding="utf-8"))


def search(
    query: str,
    top_k: int = 3,
    index_path: Path = DEFAULT_INDEX_PATH,
) -> list[dict[str, Any]]:
    payload = load_index(index_path)
    chunks = payload["chunks"]
    if not chunks:
        return []

    query_counts = Counter(expanded_query_tokens(query))
    document_frequency: Counter[str] = Counter()
    for chunk in chunks:
        document_frequency.update(set(chunk["tokens"]))

    average_length = sum(chunk["length"] for chunk in chunks) / len(chunks)
    k1 = 1.5
    b = 0.75
    scored: list[dict[str, Any]] = []

    for chunk in chunks:
        term_counts = Counter(chunk["tokens"])
        score = 0.0
        for term, query_frequency in query_counts.items():
            frequency = term_counts.get(term, 0)
            if frequency == 0:
                continue
            frequency_in_docs = document_frequency[term]
            inverse_document_frequency = math.log(
                1 + (len(chunks) - frequency_in_docs + 0.5) / (frequency_in_docs + 0.5)
            )
            denominator = frequency + k1 * (
                1 - b + b * chunk["length"] / average_length
            )
            score += query_frequency * inverse_document_frequency * (
                frequency * (k1 + 1) / denominator
            )

        if chunk["status"] == "current":
            score *= 1.12
        elif chunk["status"] == "archived":
            score *= 0.45

        if score > 0:
            result = {key: value for key, value in chunk.items() if key != "tokens"}
            result["score"] = round(score, 4)
            scored.append(result)

    scored.sort(key=lambda item: (item["score"], item["effective_date"]), reverse=True)
    return scored[:top_k]


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the local policy index")
    parser.add_argument("query")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)
    args = parser.parse_args()

    results = search(args.query, args.top_k, args.index)
    if not results:
        print("No matching section")
        return

    for rank, result in enumerate(results, start=1):
        citation = f"{result['source']}#{result['section']}"
        print(f"{rank}. score={result['score']:.4f}  {citation}")
        print(f"   status={result['status']} version={result['version']}")
        print(f"   {result['text']}")


if __name__ == "__main__":
    main()
