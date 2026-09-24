from __future__ import annotations

import argparse
import re
from dataclasses import dataclass

from ingest import tokenize
from retrieve import expanded_query_tokens, search


ABSTAIN = "现有资料里没有找到足够依据。"
DIRECT_NO_CONTEXT = "没有内部资料，无法确认这条公司规定。"
MIN_RETRIEVAL_SCORE = 3.2


@dataclass(frozen=True)
class EvalCase:
    question: str
    expected_terms: tuple[str, ...] | None
    expected_source: str | None


EVAL_CASES = (
    EvalCase("北京出差住酒店，每晚最多能报销多少？", ("650",), "travel-expense.md"),
    EvalCase("去成都出差，住宿标准是多少？", ("450",), "travel-expense.md"),
    EvalCase("一天的出差餐补是多少？", ("180",), "travel-expense.md"),
    EvalCase("酒店超标需要谁批准？", ("直属 VP", "Finance"), "travel-expense.md"),
    EvalCase("年假最多能结转几天，什么时候过期？", ("5 天", "3 月 31 日"), "leave-policy.md"),
    EvalCase("连续请三天病假要交什么？", ("医疗证明",), "leave-policy.md"),
    EvalCase("production deployment 需要什么审批？", ("两名工程师", "CI"), "engineering-handbook.md"),
    EvalCase("SEV-1 事故多久更新一次？", ("30 分钟",), "engineering-handbook.md"),
    EvalCase("6 万元采购要准备几家报价？", ("三家",), "procurement-policy.md"),
    EvalCase("供应商要访问客户数据，签约前要做什么？", ("Security review",), "security-policy.md"),
    EvalCase("半夜起飞能不能坐前舱？", ("经济舱",), "travel-expense.md"),
    EvalCase("公司每月健身补贴多少？", None, None),
)


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[。！？])\s*|\n+", text) if part.strip()]


def evidence_score(question: str, sentence: str, retrieval_score: float) -> float:
    query_terms = set(expanded_query_tokens(question))
    sentence_terms = set(tokenize(sentence))
    overlap = len(query_terms.intersection(sentence_terms))
    number_bonus = 1.0 if re.search(r"多少|几|多久|什么时候", question) and re.search(r"\d", sentence) else 0.0
    return overlap + number_bonus + retrieval_score * 0.05


def direct_answer(_: str) -> str:
    return DIRECT_NO_CONTEXT


def grounded_answer(question: str) -> dict[str, object]:
    retrieved = search(question, top_k=3)
    if not retrieved or retrieved[0]["score"] < MIN_RETRIEVAL_SCORE:
        return {"answer": ABSTAIN, "retrieved": retrieved, "citation": None}

    candidates: list[tuple[float, str, dict[str, object]]] = []
    for result in retrieved:
        for sentence in split_sentences(str(result["text"])):
            candidates.append(
                (evidence_score(question, sentence, float(result["score"])), sentence, result)
            )
    _, sentence, source = max(candidates, key=lambda item: item[0])
    citation = f"{source['source']}#{source['section']}"
    return {
        "answer": f"{sentence} [{citation}]",
        "retrieved": retrieved,
        "citation": citation,
    }


def answer_is_correct(answer: str, expected_terms: tuple[str, ...] | None) -> bool:
    if expected_terms is None:
        return answer in {ABSTAIN, DIRECT_NO_CONTEXT}
    lowered = answer.lower()
    return all(term.lower() in lowered for term in expected_terms)


def retrieval_hit(retrieved: list[dict[str, object]], expected_source: str | None) -> bool:
    if expected_source is None:
        return not retrieved or float(retrieved[0]["score"]) < MIN_RETRIEVAL_SCORE
    return any(str(item["source"]).endswith(expected_source) for item in retrieved)


def run_evaluation() -> None:
    direct_correct = 0
    rag_correct = 0
    retrieval_correct = 0

    print("| # | Question | Direct | RAG | Retrieval |")
    print("| -: | --- | :---: | :---: | :---: |")
    for index, case in enumerate(EVAL_CASES, start=1):
        direct = direct_answer(case.question)
        grounded = grounded_answer(case.question)
        direct_ok = answer_is_correct(direct, case.expected_terms)
        rag_ok = answer_is_correct(str(grounded["answer"]), case.expected_terms)
        retrieval_ok = retrieval_hit(grounded["retrieved"], case.expected_source)
        direct_correct += int(direct_ok)
        rag_correct += int(rag_ok)
        retrieval_correct += int(retrieval_ok)
        print(
            f"| {index} | {case.question} | {'pass' if direct_ok else 'fail'} "
            f"| {'pass' if rag_ok else 'fail'} | {'hit' if retrieval_ok else 'miss'} |"
        )

    total = len(EVAL_CASES)
    print()
    print(f"Direct accuracy: {direct_correct}/{total}")
    print(f"RAG accuracy: {rag_correct}/{total}")
    print(f"Retrieval success: {retrieval_correct}/{total}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local grounded policy assistant")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--question")
    group.add_argument("--eval", action="store_true")
    parser.add_argument("--mode", choices=("direct", "rag", "both"), default="both")
    args = parser.parse_args()

    if args.eval:
        run_evaluation()
        return

    if args.mode in {"direct", "both"}:
        print(f"Direct: {direct_answer(args.question)}")
    if args.mode in {"rag", "both"}:
        result = grounded_answer(args.question)
        print(f"RAG: {result['answer']}")
        if result["retrieved"]:
            print("Retrieved:")
            for item in result["retrieved"]:
                print(
                    f"- {item['score']:.4f} "
                    f"{item['source']}#{item['section']} ({item['status']}, {item['version']})"
                )


if __name__ == "__main__":
    main()
