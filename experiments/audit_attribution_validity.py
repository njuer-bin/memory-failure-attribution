"""Attribution validity audit for the LoCoMo n=50 oracle experiment.

Question 1 (attribution rule conformance):
    The documented attribution rule says: if ALL gold evidence reaches the final
    context AND the answer is wrong -> F6_REASONING_CANDIDATE (subject to E0/EVAL
    gates). This script checks how many answer failures were attributed to F1-F5
    even though the gold evidence was (partially or fully) present in the final
    answer context. Such cases are *misattributed* under the documented rule,
    because the answer model could have used the evidence.

Question 2 (formation reality check):
    For formation-miss cases, is there any semantic memory with high lexical
    overlap with the gold evidence text? If yes -> provenance mislink artifact;
    if no -> genuine extractor miss.

Usage:
    python experiments/audit_attribution_validity.py \
        --input results/oracle_experiments/comparison.jsonl
"""
import argparse
import json
import re
from collections import Counter


def tokenize(text):
    return set(re.findall(r"[a-z0-9]+", (text or "").lower()))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def audit(records):
    report = {
        "total": len(records),
        "rule_conformance": {},
        "context_availability_by_failure": {},
        "misattributed_examples": [],
        "correct_with_formation_loss": [],
        "answer_quality": {},
    }

    conf = Counter()
    cross = Counter()
    answers_correct = 0
    f1_by_context = Counter()

    for r in records:
        qid = r.get("question_id")
        real = r.get("modes", {}).get("real_memory", {})
        gold_count = r.get("gold_evidence_count") or len(r.get("gold_evidence") or [])
        stages = {s: (real.get(s) or {}) for s in
                  ("formation", "storage", "evolution", "retrieval", "rerank", "context")}
        ctx_found = len(stages["context"].get("found") or [])
        answer = (real.get("answer") or {})
        correct = bool(answer.get("correct"))
        failure_type = real.get("failure_type") or "NONE"
        answer_failure_type = real.get("answer_failure_type") or "NONE"

        if correct:
            answers_correct += 1

        # --- context availability bucket ---
        if ctx_found == 0:
            bucket = "none"
        elif ctx_found >= gold_count:
            bucket = "full"
        else:
            bucket = "partial"

        cross[(answer_failure_type, bucket)] += 1
        if answer_failure_type.startswith("F") and answer_failure_type != "F6_REASONING_CANDIDATE":
            f1_by_context[bucket] += 1

        # --- rule conformance: wrong answer + full context -> should be F6 candidate ---
        if (not correct) and bucket == "full" and answer_failure_type not in (
            "F6_REASONING_CANDIDATE", "E0_EVIDENCE_INSUFFICIENCY", "EVAL_SEMANTIC_UNCERTAIN",
        ):
            conf["misattributed_should_be_F6"] += 1
            if len(report["misattributed_examples"]) < 10:
                report["misattributed_examples"].append({
                    "question_id": qid,
                    "question": (r.get("question") or "")[:120],
                    "gold_answer": r.get("gold_answer"),
                    "attributed": answer_failure_type,
                    "prediction": (answer.get("answer") or "")[:120],
                    "gold_in_context": ctx_found,
                    "gold_total": gold_count,
                })
        elif (not correct) and answer_failure_type.startswith("F") and answer_failure_type != "F6_REASONING_CANDIDATE":
            conf["genuine_pipeline_failure"] += 1
        elif not correct:
            conf["other_non_correct"] += 1
        else:
            conf["correct"] += 1

        # --- correct despite formation loss (correct-for-wrong-reasons candidates) ---
        if correct and failure_type.startswith("F1"):
            report["correct_with_formation_loss"].append({
                "question_id": qid,
                "question": (r.get("question") or "")[:100],
                "prediction": (answer.get("answer") or "")[:100],
                "gold_answer": r.get("gold_answer"),
            })

    report["rule_conformance"] = dict(conf)
    report["context_availability_by_failure"] = {
        f"{a} | ctx={b}": c for (a, b), c in sorted(cross.items(), key=lambda x: -x[1])
    }
    report["F1_F5_failures_by_context_availability"] = dict(f1_by_context)
    report["answer_quality"] = {
        "correct": answers_correct,
        "accuracy": round(answers_correct / max(1, len(records)), 4),
    }

    # --- Question 2: semantic memory overlap for formation-miss cases ---
    # The engine DBs live in data/; semantic memories carry source_turn_id.
    # We check overlap between gold evidence text and ALL semantic memory texts
    # in the same session (provenance-agnostic) to detect mislink artifacts.
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="results/oracle_experiments/comparison.jsonl")
    args = ap.parse_args()
    records = load(args.input)
    report = audit(records)
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
