"""Diagnostic: does the verbatim retrieval bottleneck survive a real embedding?

Recomputes retrieval recall for the verbatim system with whatever embedding
backend the environment selects (e.g. ``OLLAMA_EMBEDDING_MODEL=bge-m3:latest``)
and compares it with the stored hash:384 run. Checkpoints per question so a
killed run can resume. No answer/judge calls.

Usage:
    OLLAMA_EMBEDDING_MODEL=bge-m3:latest USE_OLLAMA_EMBEDDING=1 \
        python -m experiments.check_embedding_retrieval \
        --comparison results/systems_locomo_n200_fixedgate/comparison.jsonl \
        --dataset locomo_refined_public --limit 100 \
        --out results/embedding_backend_check_locomo_n100.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from datasets.loader import iter_normalized
from experiments.memory_systems import EmbeddingProvider, VerbatimSystem, _cosine, stage_dict
from experiments.retrieval_intervention import content_tokens, rank_items


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _recall(system: VerbatimSystem, gold: list[dict[str, Any]], ranked: list[dict[str, Any]]) -> float | None:
    gold_ids = {str(x.get("evidence_id")) for x in gold if x.get("evidence_id")}
    if not gold_ids:
        return None
    search = {"retrieval": ranked[:20], "rerank": ranked[:10], "context": ranked[:10]}
    stages = stage_dict(system.stages(gold, search), gold, mode="verbatim")
    found = {str(x) for x in stages["retrieval"]["found"]}
    return len(gold_ids & found) / len(gold_ids)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--dataset", default="locomo_refined_public")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    baseline = {
        str(row["question_id"]): row
        for row in (json.loads(line) for line in Path(args.comparison).read_text(encoding="utf-8").splitlines() if line.strip())
    }
    out = Path(args.out)
    done_rows = _load_jsonl(out)
    done = {str(r["question_id"]) for r in done_rows}
    probe = EmbeddingProvider().probe()
    print("embedding backend:", probe, flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)

    for idx, record in enumerate(iter_normalized(args.dataset, limit=args.limit)):
        qid = str(record.get("question_id"))
        if qid in done or qid not in baseline:
            continue
        base_mode = baseline[qid]["modes"]["verbatim"]
        f4 = base_mode.get("answer_failure_type") == "F4_RETRIEVAL"
        question = str(record.get("question") or "")
        gold = record.get("gold_evidence") or []
        system = VerbatimSystem()
        system.ingest(record)
        qv = system.embedder.embed(question)
        ranked = sorted(system.items, key=lambda item: _cosine(qv, item["vector"]), reverse=True)
        dense = _recall(system, gold, ranked)
        hybrid = _recall(system, gold, rank_items(system.items, qv, content_tokens(question), 0.5))
        row = {
            "question_id": qid,
            "f4": f4,
            "dense_recall": dense,
            "hybrid_recall": hybrid,
            "backend": system.embedder.last_backend,
            "items": len(system.items),
        }
        done_rows.append(row)
        with out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        if (idx + 1) % 10 == 0:
            print(f"progress {idx + 1}", flush=True)

    def mean(values: list[float]) -> float | None:
        return sum(values) / len(values) if values else None

    def subset(flag: bool) -> dict[str, Any]:
        rows = [r for r in done_rows if r["f4"] is flag]
        return {
            "n": len(rows),
            "dense_recall": mean([r["dense_recall"] for r in rows if r["dense_recall"] is not None]),
            "hybrid_recall": mean([r["hybrid_recall"] for r in rows if r["hybrid_recall"] is not None]),
        }

    summary = {
        "backend_probe": probe,
        "rows": len(done_rows),
        "all": {
            "n": len(done_rows),
            "dense_recall": mean([r["dense_recall"] for r in done_rows if r["dense_recall"] is not None]),
            "hybrid_recall": mean([r["hybrid_recall"] for r in done_rows if r["hybrid_recall"] is not None]),
        },
        "f4": subset(True),
        "non_f4": subset(False),
        "backends_seen": sorted({str(r["backend"]) for r in done_rows}),
    }
    Path(str(out).replace(".jsonl", ".json")).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
