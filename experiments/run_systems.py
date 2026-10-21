"""Run cross-system memory comparisons and emit per-system fingerprints.

Each selected system ingests the same conversation, answers the same question,
and is scored by the same judge, gate and attribution protocol. The output is a
``comparison.jsonl`` plus a ``summary.json`` with per-system stage recall,
first-loss distribution, semantic accuracy and E0 rate — the Failure
Fingerprint inputs.

Usage:
    python -m experiments.run_systems --dataset evolution_probe \
        --systems verbatim,summary --limit 40 \
        --out-dir results/systems_evolution_probe
"""
from __future__ import annotations

import argparse
import json
import time
import traceback
from pathlib import Path
from typing import Any

from datasets.loader import iter_normalized
from evaluation.attribution import attribute_failure
from evaluation.lifecycle_metrics import MEASURED_STAGES, stage_recall, summarize_traces
from experiments import run_oracle_experiments as runner
from experiments.memory_systems import SYSTEMS, stage_dict


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


def _cap_context(items: list[dict[str, Any]], budget: int) -> list[dict[str, Any]]:
    """Give every system the same context character budget.

    Without this, session-sized summary items receive far more text than
    turn-sized verbatim items at the same top-k.
    """
    kept: list[dict[str, Any]] = []
    used = 0
    for item in items:
        size = len(str(item.get("content") or ""))
        if kept and used + size > budget:
            break
        kept.append(item)
        used += size
        if used >= budget:
            break
    return kept


def _summary(rows: list[dict[str, Any]], systems: tuple[str, ...]) -> dict[str, Any]:
    output: dict[str, Any] = {"systems": {}}
    for name in systems:
        traces = []
        for row in rows:
            mode = (row.get("modes") or {}).get(name)
            if not mode:
                continue
            traces.append({"gold_evidence": row.get("gold_evidence") or [], **mode})
        if not traces:
            continue
        summary = summarize_traces(traces)
        answers = [
            (mode.get("answer") or {}).get("semantic_correct")
            for mode in ((row.get("modes") or {}).get(name) for row in rows)
            if mode
        ]
        judged = [a for a in answers if a is not None]
        gates = [
            ((mode.get("evidence_sufficiency") or {}).get("status"))
            for mode in ((row.get("modes") or {}).get(name) for row in rows)
            if mode
        ]
        output["systems"][name] = {
            **summary,
            "stage_recall": {
                stage: value for stage, value in summary["stage_recall"].items()
                if stage in MEASURED_STAGES or value is not None
            },
            "semantic_accuracy": (sum(1 for a in judged if a) / len(judged)) if judged else None,
            "semantic_judged": len(judged),
            "answer_failure_distribution": {
                failure or "none": sum(
                    1 for row in rows
                    if ((row.get("modes") or {}).get(name) or {}).get("answer_failure_type") == failure
                )
                for failure in {
                    ((row.get("modes") or {}).get(name) or {}).get("answer_failure_type")
                    for row in rows if (row.get("modes") or {}).get(name)
                }
            },
            "gate_distribution": {
                status: gates.count(status) for status in set(gates)
            },
        }
    return output


def run(dataset: str, systems: tuple[str, ...], limit: int | None, out: Path,
        resume: bool, context_chars: int = 6000) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    jsonl = out / "comparison.jsonl"
    rows = _load_jsonl(jsonl) if resume else []
    jsonl.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
        encoding="utf-8",
    )
    done = {str(r.get("question_id")) for r in rows}
    started = time.perf_counter()
    errors = 0

    for idx, record in enumerate(iter_normalized(dataset, limit=limit)):
        qid = str(record.get("question_id"))
        if qid in done:
            continue
        gold = record.get("gold_evidence") or []
        reference = record.get("answer") or ""
        row: dict[str, Any] = {
            "question_id": qid,
            "question": record.get("question"),
            "gold_answer": reference,
            "gold_evidence": gold,
            "task_type": record.get("task_type") or [],
            "modes": {},
        }
        print(f"[{idx + 1}] {qid}", flush=True)
        try:
            for name in systems:
                system = SYSTEMS[name]()
                system.ingest(record)
                search = system.search(str(record.get("question") or ""))
                search["context"] = _cap_context(search["context"], context_chars)
                stages = stage_dict(system.stages(gold, search), gold, mode=name)
                context = search["context"]
                answer = runner._score_mode_answer(str(record.get("question") or ""), reference, context)
                answer = runner._semantic_eval(str(record.get("question") or ""), answer, gold, reference)
                gate = runner._evidence_sufficiency(str(record.get("question") or ""), reference, gold)
                failure = attribute_failure(answer, gate, stages, gold, mode=name)
                row["modes"][name] = {
                    **stages,
                    "answer": answer,
                    "evidence_sufficiency": gate,
                    "answer_failure_type": failure,
                }
        except Exception as exc:
            errors += 1
            print(f"[{idx + 1}] ERROR {type(exc).__name__}: {exc}", flush=True)
            traceback.print_exc()
            continue
        rows.append(row)
        with jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            fh.flush()
        (out / "progress.json").write_text(json.dumps({
            "status": "running", "completed": len(rows), "errors": errors,
            "elapsed_seconds": time.perf_counter() - started,
        }, indent=2), encoding="utf-8")

    summary = {
        "run_metadata": runner._run_metadata(dataset, limit or len(rows)),
        "systems": list(systems),
        "errors": errors,
        "results": _summary(rows, systems),
    }
    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "progress.json").write_text(json.dumps({
        "status": "completed", "completed": len(rows), "errors": errors,
        "elapsed_seconds": time.perf_counter() - started,
    }, indent=2), encoding="utf-8")
    print(json.dumps(summary["results"], ensure_ascii=False, indent=2))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--systems", default="verbatim,summary")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--context-chars", type=int, default=6000)
    args = parser.parse_args()
    systems = tuple(s.strip() for s in args.systems.split(",") if s.strip())
    unknown = [s for s in systems if s not in SYSTEMS]
    if unknown:
        raise SystemExit(f"unknown systems {unknown}; choose from {sorted(SYSTEMS)}")
    run(args.dataset, systems, args.limit, Path(args.out_dir), args.resume,
        args.context_chars)


if __name__ == "__main__":
    main()
