"""Stage-targeted retrieval-repair intervention (pre-registered 2026-10-26).

See ``docs/research/2026-10-26-intervention-a-retrieval.md``. The verbatim
system ranks stored turns by hash-embedding cosine. The repair replaces that
score with a deterministic hybrid of cosine and question-token overlap, keeping
the candidate pool, top-k and context budget fixed so any gain is attributable
to ranking.

Arms:

- ``placebo``: re-answer the baseline ``F4_RETRIEVAL`` questions with the
  unchanged dense ranking (retest floor);
- ``first_loss``: hybrid ranking on those same questions;
- ``agnostic``: hybrid ranking on every question.

Routing uses only the stored baseline failure label, never gold.

Usage:
    python -m experiments.retrieval_intervention \
        --comparison results/systems_locomo_n200_fixedgate/comparison.jsonl \
        --dataset locomo_refined_public --limit 100 \
        --out-dir results/retrieval_intervention_locomo_n100
"""
from __future__ import annotations

import argparse
import json
import re
import time
import traceback
from pathlib import Path
from typing import Any

from datasets.loader import iter_normalized
from evaluation.attribution import attribute_failure
from evaluation.paired_stats import mcnemar_exact, paired_bootstrap_diff, paired_table
from experiments import run_oracle_experiments as runner
from experiments.memory_systems import VerbatimSystem, _cosine, stage_dict
from experiments.run_systems import _cap_context

_TOKEN = re.compile(r"[a-z0-9]+")
_STOP = set(
    "the a an of to in on at for and or is are was were be been being with by "
    "from that this these those it its as into their his her she he they them "
    "we you your i me my our not do does did no if then than about what when "
    "where who whom which why how".split()
)
F4 = "F4_RETRIEVAL"


def content_tokens(text: str) -> set[str]:
    return {w for w in _TOKEN.findall((text or "").lower()) if w not in _STOP and len(w) > 2}


def lexical_overlap(question_tokens: set[str], content: str) -> float:
    if not question_tokens:
        return 0.0
    item_tokens = set(_TOKEN.findall((content or "").lower()))
    return len(question_tokens & item_tokens) / len(question_tokens)


def rank_items(items: list[dict[str, Any]], question_vector: list[float],
               question_tokens: set[str], alpha: float) -> list[dict[str, Any]]:
    """Rank items by (1-alpha)*cosine + alpha*lexical overlap.

    ``alpha=0`` reproduces the baseline dense ranking exactly.
    """
    scored = []
    for item in items:
        score = _cosine(question_vector, item["vector"])
        if alpha:
            score = ((1.0 - alpha) * score
                     + alpha * lexical_overlap(question_tokens, item.get("content") or ""))
        scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored]


def _stages(system: VerbatimSystem, gold: list[dict[str, Any]],
            ranked: list[dict[str, Any]], candidate_k: int, top_k: int,
            context_chars: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    search = {
        "retrieval": ranked[:candidate_k],
        "rerank": ranked[:top_k],
        "context": _cap_context(ranked[:top_k], context_chars),
    }
    return stage_dict(system.stages(gold, search), gold, mode="verbatim"), search["context"]


def _recall(stages: dict[str, Any], gold: list[dict[str, Any]]) -> float | None:
    gold_ids = {str(x.get("evidence_id")) for x in gold if x.get("evidence_id")}
    if not gold_ids:
        return None
    found = {str(x) for x in stages.get("retrieval", {}).get("found", [])}
    return len(gold_ids & found) / len(gold_ids)


def _answer(question: str, reference: str, gold: list[dict[str, Any]],
            context: list[dict[str, Any]]) -> dict[str, Any]:
    answer = runner._score_mode_answer(question, reference, context)
    return runner._semantic_eval(question, answer, gold, reference)


def _outcome(answer: dict[str, Any], gate: dict[str, Any],
             stages: dict[str, Any], gold: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "answer": answer.get("answer"),
        "semantic_correct": answer.get("semantic_correct"),
        "failure": attribute_failure(answer, gate, stages, gold, mode="verbatim"),
    }


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


def run(comparison: Path, dataset: str, limit: int, out: Path,
        alpha: float = 0.5, candidate_k: int = 20, top_k: int = 10,
        context_chars: int = 6000, resume: bool = False) -> dict[str, Any]:
    baseline = {str(r["question_id"]): r for r in _load_jsonl(comparison)}
    out.mkdir(parents=True, exist_ok=True)
    jsonl = out / "interventions.jsonl"
    rows = _load_jsonl(jsonl) if resume else []
    done = {str(r["question_id"]) for r in rows}
    if not resume:
        jsonl.write_text("", encoding="utf-8")
    started = time.perf_counter()
    errors = 0
    records = list(iter_normalized(dataset, limit=limit))
    for idx, record in enumerate(records):
        qid = str(record.get("question_id"))
        if qid in done or qid not in baseline:
            continue
        question = str(record.get("question") or "")
        reference = str(record.get("answer") or "")
        gold = record.get("gold_evidence") or []
        base_mode = baseline[qid]["modes"]["verbatim"]
        gate = base_mode.get("evidence_sufficiency") or {}
        baseline_failure = base_mode.get("answer_failure_type")
        is_f4 = baseline_failure == F4
        print(f"[{idx + 1}] {qid}", flush=True)
        try:
            system = VerbatimSystem()
            system.ingest(record)
            qvec = system.embedder.embed(question)
            qtokens = content_tokens(question)
            dense = rank_items(system.items, qvec, qtokens, 0.0)
            hybrid = rank_items(system.items, qvec, qtokens, alpha)
            dense_stages, dense_context = _stages(
                system, gold, dense, candidate_k, top_k, context_chars)
            hybrid_stages, hybrid_context = _stages(
                system, gold, hybrid, candidate_k, top_k, context_chars)

            arms: dict[str, Any] = {}
            if is_f4:
                answer = _answer(question, reference, gold, dense_context)
                arms["placebo"] = _outcome(answer, gate, dense_stages, gold)
            answer = _answer(question, reference, gold, hybrid_context)
            repaired = _outcome(answer, gate, hybrid_stages, gold)
            arms["agnostic"] = repaired
            if is_f4:
                arms["first_loss"] = repaired
            row = {
                "question_id": qid,
                "baseline_failure": baseline_failure,
                "f4": is_f4,
                "retrieval_recall": {
                    "dense": _recall(dense_stages, gold),
                    "hybrid": _recall(hybrid_stages, gold),
                },
                "stored_baseline_correct": (base_mode.get("answer") or {}).get("semantic_correct"),
                "arms": arms,
            }
        except Exception as exc:
            errors += 1
            print(f"[{idx + 1}] ERROR {type(exc).__name__}: {exc}", flush=True)
            traceback.print_exc()
            continue
        rows.append(row)
        with jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        (out / "progress.json").write_text(json.dumps({
            "status": "running", "completed": len(rows), "errors": errors,
            "elapsed_seconds": time.perf_counter() - started,
        }, indent=2), encoding="utf-8")

    summary = _summary(rows, alpha)
    summary["errors"] = errors
    summary["comparison"] = str(comparison)
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "progress.json").write_text(json.dumps({
        "status": "completed", "completed": len(rows), "errors": errors,
        "elapsed_seconds": time.perf_counter() - started,
    }, indent=2), encoding="utf-8")
    return summary


def _summary(rows: list[dict[str, Any]], alpha: float) -> dict[str, Any]:
    f4 = [r for r in rows if r["f4"]]
    placebo = [(r["arms"].get("placebo") or {}).get("semantic_correct") for r in f4]
    first = [(r["arms"].get("first_loss") or {}).get("semantic_correct") for r in f4]
    table = paired_table(placebo, first)
    mcnemar = mcnemar_exact(placebo, first)
    bootstrap = paired_bootstrap_diff(first, placebo)  # repair - baseline
    net = table["n01"] - table["n10"]

    def acc(values: list[Any]) -> float | None:
        clean = [v for v in values if v is not None]
        return sum(1 for v in clean if v) / len(clean) if clean else None

    dense_recall = [r["retrieval_recall"]["dense"] for r in f4
                    if r["retrieval_recall"]["dense"] is not None]
    hybrid_recall = [r["retrieval_recall"]["hybrid"] for r in f4
                     if r["retrieval_recall"]["hybrid"] is not None]
    non_f4 = [r for r in rows if not r["f4"]]
    return {
        "alpha": alpha,
        "rows": len(rows),
        "f4_subset": len(f4),
        "primary_f4": {
            "placebo_correct": sum(1 for v in placebo if v is True),
            "first_loss_correct": sum(1 for v in first if v is True),
            "table": table,
            "net_flips": net,
            "mcnemar": mcnemar,
            "bootstrap": bootstrap,
        },
        "retrieval_recall_f4": {
            "dense": sum(dense_recall) / len(dense_recall) if dense_recall else None,
            "hybrid": sum(hybrid_recall) / len(hybrid_recall) if hybrid_recall else None,
        },
        "overall": {
            "stored_baseline_accuracy": acc([r.get("stored_baseline_correct") for r in rows]),
            "agnostic_accuracy": acc([(r["arms"].get("agnostic") or {}).get("semantic_correct") for r in rows]),
        },
        "non_f4_agnostic": {
            "n": len(non_f4),
            "stored_baseline_correct": sum(
                1 for r in non_f4 if r.get("stored_baseline_correct") is True),
            "agnostic_correct": sum(
                1 for r in non_f4 if (r["arms"].get("agnostic") or {}).get("semantic_correct") is True),
        },
        "decision": {
            "success": bool(net >= 6 and (bootstrap.get("ci_low") or 0.0) > 0),
            "rule": "net_flips >= 6 and bootstrap CI low > 0 on the F4 subset",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--dataset", default="locomo_refined_public")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--alpha", type=float, default=0.5)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--context-chars", type=int, default=6000)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    summary = run(Path(args.comparison), args.dataset, args.limit, Path(args.out_dir),
                  alpha=args.alpha, candidate_k=args.candidate_k, top_k=args.top_k,
                  context_chars=args.context_chars, resume=args.resume)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
