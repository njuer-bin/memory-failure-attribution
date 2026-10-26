"""Build the round-5 blind stage-annotation workbook (pilot or full).

For each question and each requested system, dump the memory items the system
held at every lifecycle stage as short previews, and write a blinded workbook
whose only judgement is "first stage at which the gold evidence is absent".
Automatic labels and system identity go into a separate hidden key.

Formation/storage/evolution previews are ranked by overlap with the gold
evidence text (so the annotator does not have to scan 500 items); the
retrieval/rerank/context previews are the system's own ordered context items.

Usage:
    python -m experiments.build_stage_annotation_package \
        --comparison results/systems_locomo_n200_fixedgate/comparison.jsonl \
        --limit 20 --systems semantic,verbatim \
        --out results/annotation_package
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from datasets.loader import iter_normalized
from evaluation.attribution import first_missing_stage
from experiments.memory_systems import SYSTEMS, stage_dict
from experiments.retrieval_intervention import content_tokens

STAGE_ORDER = ("formation", "storage", "evolution", "retrieval", "rerank", "context")
README = """# Round 5 — blind stage attribution (pilot)

For each row you see one question, its reference answer, the gold evidence, and
the memory items a system held at six lifecycle stages (previews, truncated).
Mark the **first stage at which the gold evidence needed for the reference
answer is no longer present**. Use only this row.

- `formation` / `storage` / `evolution` previews are the items most textually
  related to the gold evidence (not the full store).
- `retrieval` / `rerank` / `context` previews are the system's own ordered
  context at that stage.
- Mark `none` when every stage still contains the needed evidence.
- Mark `E0` when the gold evidence itself does not establish the reference
  answer (the question is unanswerable from the benchmark evidence).
- Mark `uncertain` when the previews are insufficient to decide; add a note.

System identity is hidden (A/B). Do not open the key. Two annotators work
independently; disagreements are adjudicated blind. Every non-`none` choice
needs a one-line note naming the absent evidence or the stage where it vanished.

Pilot acceptance: Cohen's kappa >= 0.70 on the stage label. If the pilot falls
short, the task shape is revised before the full 100 questions.
"""


def _load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _preview(items: list[dict[str, Any]], k: int = 5, chars: int = 300) -> str:
    return " || ".join(
        f"[{i + 1}] {str(item.get('content') or '')[:chars]}"
        for i, item in enumerate(items[:k])
    )


def _rank_by_gold(items: list[dict[str, Any]], gold_text: str, k: int = 5) -> list[dict[str, Any]]:
    gold_tokens = content_tokens(gold_text)
    return sorted(
        items,
        key=lambda item: len(gold_tokens & content_tokens(str(item.get("content") or ""))),
        reverse=True,
    )[:k]


def _auto_first_loss(stages: dict[str, Any], gold: list[dict[str, Any]]) -> str:
    gold_ids = {str(x.get("evidence_id")) for x in gold if x.get("evidence_id")}
    if not gold_ids:
        return "E0"
    return first_missing_stage(stages, gold_ids) or "none"


def build(comparison: Path, limit: int, systems: list[str], out: Path) -> None:
    baseline = {str(r["question_id"]): r for r in _load(comparison)}
    records = list(iter_normalized("locomo_refined_public", limit=limit))
    workbook: list[dict[str, str]] = []
    key: list[dict[str, str]] = []
    for qi, record in enumerate(records, start=1):
        qid = str(record.get("question_id"))
        if qid not in baseline:
            continue
        question = str(record.get("question") or "")
        reference = str(record.get("answer") or "")
        gold = record.get("gold_evidence") or []
        gold_text = "\n".join(str(g.get("text") or "") for g in gold)
        gold_block = "\n".join(f"[{i + 1}] {str(g.get('text') or '')}" for i, g in enumerate(gold))
        for si, name in enumerate(systems):
            system = SYSTEMS[name]()
            system.ingest(record)
            search = system.search(question, candidate_k=20, top_k=10)
            raw_stages = system.stages(gold, search) or {}
            stages = stage_dict(raw_stages, gold, mode=name)
            previews = {}
            for stage in STAGE_ORDER:
                raw = raw_stages.get(stage) or []
                if stage in ("formation", "storage", "evolution"):
                    items = _rank_by_gold(raw, gold_text)
                else:
                    items = raw
                previews[stage] = _preview(items)
            row_id = f"q{qi:03d}-{chr(ord('A') + si)}"
            workbook.append({
                "row_id": row_id,
                "system_blind": chr(ord("A") + si),
                "question": question,
                "reference_answer": reference,
                "gold_evidence": gold_block,
                **{f"{stage}_preview": previews[stage] for stage in STAGE_ORDER},
                "annotated_first_loss_stage": "",
                "confidence": "",
                "notes": "",
            })
            key.append({
                "row_id": row_id,
                "question_id": qid,
                "system": name,
                "system_blind": chr(ord("A") + si),
                "auto_first_loss": _auto_first_loss(stages, gold),
                "auto_failure_type": str(
                    ((baseline[qid]["modes"].get(name) or {}).get("answer_failure_type")) or ""),
                "gate_status": str(
                    (((baseline[qid]["modes"].get(name) or {}).get("evidence_sufficiency") or {})
                     .get("status")) or ""),
            })
        print(f"[{qi}/{len(records)}] {qid}", flush=True)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "round5_stage_pilot.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(workbook[0]))
        writer.writeheader()
        writer.writerows(workbook)
    with (out / "round5_stage_pilot_key.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(key[0]))
        writer.writeheader()
        writer.writerows(key)
    (out / "README_round5.md").write_text(README, encoding="utf-8")
    print(f"wrote {len(workbook)} rows for {len(records)} questions")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--systems", default="semantic,verbatim")
    parser.add_argument("--out", default="results/annotation_package")
    args = parser.parse_args()
    systems = [s.strip() for s in args.systems.split(",") if s.strip()]
    unknown = [s for s in systems if s not in SYSTEMS]
    if unknown:
        raise SystemExit(f"unknown systems {unknown}; choose from {sorted(SYSTEMS)}")
    build(Path(args.comparison), args.limit, systems, Path(args.out))


if __name__ == "__main__":
    main()
