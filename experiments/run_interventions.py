"""Run the P2 stage-targeted intervention experiment.

Each baseline row is re-ingested once. The runner then produces, under the
same answer model, judge and deterministic floors:

- a freshly generated baseline answer (no repair);
- the repaired answer for every requested routing arm (``first_loss``,
  ``path``, ``agnostic``).

Routing uses only the stored diagnostic trace, never the gold answer. The
summary reports paired accuracy gains on each arm's targeted subset with exact
McNemar and a paired bootstrap CI.
"""
from __future__ import annotations

import argparse
import json
import time
import traceback
from pathlib import Path
from typing import Any

from datasets.loader import iter_normalized
from evaluation.answer_generation import (
    generate_answer,
    generate_self_checked_answer,
    score_answer,
)
from evaluation.paired_stats import mcnemar_exact, paired_bootstrap_diff
from experiments import run_oracle_experiments as runner
from experiments.interventions import arm_target, write_through_verbatim
from memory_engine.models import SearchRequest
from tracing.engine_trace import retrieval_artifacts

ROOT = Path(__file__).resolve().parents[1]
ALL_ARMS = ("first_loss", "path", "agnostic")
KNOWN_ARMS = ALL_ARMS + ("placebo",)


def log(message: str) -> None:
    print(message, flush=True)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and row.get("question_id"):
            rows.append(row)
    return rows


def _search(engine: Any, user_id: str, question: str, top_k: int, type_cap: int) -> list[dict[str, Any]]:
    results = engine.search(SearchRequest(
        query=question, user_id=user_id, top_k=top_k, multi_hop=True,
        evidence_type_cap=type_cap,
    ))
    return engine.last_search_trace.get("context") or retrieval_artifacts(results)


def _answer(question: str, reference: str, context: list[dict[str, Any]], *, self_check: bool) -> dict[str, Any]:
    try:
        text = (
            generate_self_checked_answer(question, context)
            if self_check else generate_answer(question, context)
        )
    except Exception as exc:
        return {
            "answer": None, "correct": None, "exact_match": None,
            "token_f1": None, "threshold": None,
            "model_error": f"{type(exc).__name__}: {exc}",
        }
    return {"answer": text, **score_answer(text, reference, context=context)}


def _semantic(question: str, answer: dict[str, Any], gold: list[dict[str, Any]], reference: str, gate: dict[str, Any]) -> dict[str, Any]:
    answer = runner._semantic_eval(question, answer, gold, reference)
    answer["gate_status"] = gate.get("status")
    return answer


def _context_plan(targets: dict[str, str | None]) -> dict[str, bool]:
    wanted = {t for t in targets.values() if t}
    return {
        "formation": "formation" in wanted,
        "context": "context" in wanted,
        "retrieval": "retrieval" in wanted,
        "all": "all" in wanted,
    }


def run_record(
    record: dict[str, Any],
    idx: int,
    baseline_row: dict[str, Any],
    arms: tuple[str, ...],
) -> list[dict[str, Any]]:
    question = record["question"]
    reference = record.get("answer", "")
    gold = baseline_row.get("gold_evidence") or []
    gate = (
        baseline_row.get("modes", {}).get("real_memory", {}).get("evidence_sufficiency")
        or {}
    )
    stored_verdict = (
        baseline_row.get("modes", {}).get("real_memory", {})
        .get("answer", {}).get("semantic_correct")
    )

    targets = {arm: arm_target(baseline_row, arm) for arm in arms}
    if not any(targets.values()):
        return [
            {
                "question_id": baseline_row.get("question_id"), "arm": arm,
                "target_stage": None, "skipped": True,
                "stored_baseline_semantic_correct": stored_verdict,
                "gate_status": gate.get("status"),
            }
            for arm in arms
        ]

    engine, user_id = runner._real_engine(record, idx)
    plan = _context_plan(targets)

    # Baseline and pre-write-through context repairs share one engine state.
    base_context = _search(engine, user_id, question, top_k=10, type_cap=3)
    seen_contexts: dict[str, list[dict[str, Any]]] = {"baseline": base_context}
    if plan["context"]:
        seen_contexts["context"] = _search(engine, user_id, question, top_k=20, type_cap=8)
    if plan["retrieval"]:
        seen_contexts["retrieval"] = _search(engine, user_id, question, top_k=20, type_cap=3)

    if plan["formation"]:
        write_through_verbatim(engine, user_id)
        seen_contexts["formation"] = _search(engine, user_id, question, top_k=10, type_cap=3)
    if plan["all"]:
        write_through_verbatim(engine, user_id)
        seen_contexts["all"] = _search(engine, user_id, question, top_k=20, type_cap=8)

    def answer_for(stage: str) -> dict[str, Any]:
        if stage == "placebo":
            # Noise floor: a second unmodified answer under the same protocol.
            answer = _answer(question, reference, base_context, self_check=False)
            return _semantic(question, answer, gold, reference, gate)
        context = base_context if stage == "reasoning" else seen_contexts[stage]
        self_check = stage in {"reasoning", "all"}
        answer = _answer(question, reference, context, self_check=self_check)
        return _semantic(question, answer, gold, reference, gate)

    baseline_answer = _semantic(
        question, _answer(question, reference, base_context, self_check=False),
        gold, reference, gate,
    )

    cache: dict[str, dict[str, Any]] = {"baseline": baseline_answer}
    answers = {}
    for arm, stage in targets.items():
        if stage is None:
            answers[arm] = None
            continue
        if stage == "placebo":
            # Never cached: the point is a second independent draw.
            answers[arm] = answer_for("placebo")
            continue
        if stage not in cache:
            cache[stage] = answer_for(stage)
        answers[arm] = cache[stage]

    rows = []
    for arm in arms:
        rows.append({
            "question_id": baseline_row.get("question_id"),
            "arm": arm,
            "target_stage": targets.get(arm),
            "stored_baseline_semantic_correct": stored_verdict,
            "baseline": baseline_answer,
            "repaired": answers.get(arm),
            "gate_status": gate.get("status"),
        })
    return rows


def _summary(rows: list[dict[str, Any]], arms: tuple[str, ...]) -> dict[str, Any]:
    output: dict[str, Any] = {"arms": {}, "target_breakdown": {}}
    for arm in arms:
        arm_rows = [r for r in rows if r.get("arm") == arm and not r.get("skipped")]
        targeted = [r for r in arm_rows if r.get("target_stage")]
        a = [(r.get("baseline") or {}).get("semantic_correct") for r in targeted]
        b = [(r.get("repaired") or {}).get("semantic_correct") for r in targeted]
        paired = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
        aa = [x for x, _ in paired]
        bb = [y for _, y in paired]
        output["arms"][arm] = {
            "scored_rows": len(arm_rows),
            "targeted_rows": len(targeted),
            "paired_rows": len(paired),
            "baseline_correct": sum(1 for x in aa if x),
            "repaired_correct": sum(1 for y in bb if y),
            "accuracy_gain": (
                (sum(1 for y in bb if y) - sum(1 for x in aa if x)) / len(paired)
                if paired else None
            ),
            "mcnemar": mcnemar_exact(aa, bb),
            "bootstrap": paired_bootstrap_diff(aa, bb),
        }
        for stage in sorted({r.get("target_stage") for r in targeted}):
            stage_rows = [r for r in targeted if r.get("target_stage") == stage]
            sa = [(r.get("baseline") or {}).get("semantic_correct") for r in stage_rows]
            sb = [(r.get("repaired") or {}).get("semantic_correct") for r in stage_rows]
            pairs = [(x, y) for x, y in zip(sa, sb) if x is not None and y is not None]
            output["target_breakdown"][f"{arm}:{stage}"] = {
                "rows": len(pairs),
                "baseline_correct": sum(1 for x, _ in pairs if x),
                "repaired_correct": sum(1 for _, y in pairs if y),
                "mcnemar": mcnemar_exact([x for x, _ in pairs], [y for _, y in pairs]),
                "bootstrap": paired_bootstrap_diff([x for x, _ in pairs], [y for _, y in pairs]),
            }
    return output


def run(
    baseline: Path,
    dataset: str,
    out: Path,
    arms: tuple[str, ...],
    limit: int | None,
    resume: bool,
) -> dict[str, Any]:
    baseline_rows = _load_jsonl(baseline)
    if limit:
        baseline_rows = baseline_rows[:limit]
    if not baseline_rows:
        raise SystemExit(f"no baseline rows in {baseline}")
    out.mkdir(parents=True, exist_ok=True)
    jsonl = out / "interventions.jsonl"
    rows = _load_jsonl(jsonl) if resume else []
    rows = [r for r in rows if r.get("question_id")]
    jsonl.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )
    done = {(str(r.get("question_id")), str(r.get("arm"))) for r in rows}
    by_id = {str(r.get("question_id")): r for r in baseline_rows}

    started = time.perf_counter()
    errors = 0
    for idx, record in enumerate(iter_normalized(dataset, limit=limit or len(baseline_rows))):
        qid = str(record.get("question_id"))
        baseline_row = by_id.get(qid)
        if baseline_row is None:
            continue
        if all((qid, arm) in done for arm in arms):
            continue
        log(f"[{idx + 1}] intervention question_id={qid}")
        try:
            new_rows = run_record(record, idx, baseline_row, arms)
            for row in new_rows:
                if (str(row.get("question_id")), str(row.get("arm"))) in done:
                    continue
                rows.append(row)
                with jsonl.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    f.flush()
        except Exception as exc:
            errors += 1
            log(f"[{idx + 1}] ERROR {type(exc).__name__}: {exc}")
            traceback.print_exc()
        (out / "progress.json").write_text(json.dumps({
            "status": "running", "completed": len({r['question_id'] for r in rows}),
            "errors": errors, "elapsed_seconds": time.perf_counter() - started,
        }, indent=2), encoding="utf-8")

    summary = {
        "run_metadata": runner._run_metadata(dataset, limit or len(baseline_rows)),
        "baseline": str(baseline),
        "arms": list(arms),
        "errors": errors,
        "results": _summary(rows, arms),
    }
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "progress.json").write_text(json.dumps({
        "status": "completed", "completed": len({r['question_id'] for r in rows}),
        "errors": errors, "elapsed_seconds": time.perf_counter() - started,
    }, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True, help="comparison.jsonl of the baseline run")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--arms", default=",".join(ALL_ARMS))
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    arms = tuple(a.strip() for a in args.arms.split(",") if a.strip())
    for arm in arms:
        if arm not in KNOWN_ARMS:
            raise SystemExit(f"unknown arm {arm!r}; choose from {KNOWN_ARMS}")
    run(
        Path(args.baseline), args.dataset, Path(args.out_dir),
        arms, args.limit, args.resume,
    )


if __name__ == "__main__":
    main()
