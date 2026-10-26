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
README = """# Round 5 — blind stage attribution (v2 pilot)

For each row you see one question, its reference answer, the gold evidence with
its session dates, and the memory items a system held at each lifecycle stage.
Mark the **first stage at which the gold evidence needed for the reference
answer is no longer present**.

## Labels (8 classes; `evolution` is not measured and is excluded)

`formation | storage | retrieval | rerank | context | none | E0 | uncertain`

- `none`: every measured stage still contains the needed evidence.
- `E0`: the gold evidence itself does not establish the reference answer
  (use the dates shown in `gold_evidence_dates` to resolve relative time).
- `uncertain`: the previews are insufficient to decide; add a note.

## What the previews mean

- `retrieval`: the system's full top-20 candidates (N shown in the header).
- `rerank` / `context`: the system's full top-10 (N shown in the header).
- `formation` / `storage`: two views of the stored items — the first 10 in
  session order and the top 10 by overlap with the gold evidence, with the
  total count in the header. **Operational rule: if the gold evidence does not
  appear in either view, treat the stage as missing.** This is a defined
  criterion, not a claim that the full store lacks it; say so in the analysis.
- `evolution` is excluded because it is unmeasured in both systems (empty for
  verbatim, constant for semantic). Do not use it as a label.

For verbatim rows the retrieval/rerank/context previews are the same ranking at
different cutoffs (20 / 10 / 10); that is a property of the system, not a
package error.

## Procedure

Two annotators, independent and blind; system identity is A/B and the key is
hidden. Use only the row. Do not open the key. Every non-`none` choice needs a
one-line note naming the absent evidence or the stage where it vanished.

Pilot acceptance: Cohen's kappa >= 0.70 on the 8-class stage label (also report
kappa on the classes actually used). If the pilot falls short, revise the task
shape before the full 100 questions.
"""


def _load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _preview(items: list[dict[str, Any]], k: int | None = None, chars: int = 300) -> str:
    shown = items if k is None else items[:k]
    return " || ".join(
        f"[{i + 1}] {str(item.get('content') or '')[:chars]}"
        for i, item in enumerate(shown)
    )


def _rank_by_gold(items: list[dict[str, Any]], gold_text: str, k: int = 10) -> list[dict[str, Any]]:
    gold_tokens = content_tokens(gold_text)
    return sorted(
        items,
        key=lambda item: len(gold_tokens & content_tokens(str(item.get("content") or ""))),
        reverse=True,
    )[:k]


def _stage_preview(stage: str, raw: list[dict[str, Any]], gold_text: str,
                   candidate_k: int, top_k: int, chars: int = 200) -> str:
    if stage == "evolution":
        return "NOT MEASURED — excluded from the label set"
    if stage in ("formation", "storage"):
        ordered = raw[:10]
        gold_ranked = _rank_by_gold(raw, gold_text, 10)
        return (
            f"N={len(raw)}; session-order first {len(ordered)}:\n"
            + _preview(ordered, chars=chars)
            + f"\n--- gold-overlap top {len(gold_ranked)}:\n"
            + _preview(gold_ranked, chars=chars)
        )
    limit = candidate_k if stage == "retrieval" else top_k
    shown = raw[:limit]
    return f"N={len(raw)}; top {len(shown)}:\n" + _preview(shown, chars=chars)


def _auto_first_loss(stages: dict[str, Any], gold: list[dict[str, Any]]) -> str:
    gold_ids = {str(x.get("evidence_id")) for x in gold if x.get("evidence_id")}
    if not gold_ids:
        return "E0"
    return first_missing_stage(stages, gold_ids) or "none"


def build(comparison: Path, limit: int, systems: list[str], out: Path,
          tag: str = "pilot_v2") -> None:
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
        gold_block = "\n".join(
            f"[{i + 1}] ({str(g.get('source_id') or '?')}, "
            f"{str(g.get('timestamp') or 'no date')}) {str(g.get('text') or '')}"
            for i, g in enumerate(gold)
        )
        gold_dates = "\n".join(
            f"[{i + 1}] {str(g.get('source_id') or '?')} | "
            f"{str(g.get('timestamp') or 'no date')}"
            for i, g in enumerate(gold)
        )
        for si, name in enumerate(systems):
            system = SYSTEMS[name]()
            system.ingest(record)
            search = system.search(question, candidate_k=20, top_k=10)
            raw_stages = system.stages(gold, search) or {}
            stages = stage_dict(raw_stages, gold, mode=name)
            previews = {}
            for stage in STAGE_ORDER:
                raw = raw_stages.get(stage) or []
                previews[stage] = _stage_preview(stage, raw, gold_text, 20, 10)
            row_id = f"q{qi:03d}-{chr(ord('A') + si)}"
            workbook.append({
                "row_id": row_id,
                "system_blind": chr(ord("A") + si),
                "question": question,
                "reference_answer": reference,
                "gold_evidence": gold_block,
                "gold_evidence_dates": gold_dates,
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
    with (out / f"round5_stage_{tag}.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(workbook[0]))
        writer.writeheader()
        writer.writerows(workbook)
    with (out / f"round5_stage_{tag}_key.csv").open("w", encoding="utf-8", newline="") as fh:
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
    parser.add_argument("--tag", default="pilot_v2")
    args = parser.parse_args()
    systems = [s.strip() for s in args.systems.split(",") if s.strip()]
    unknown = [s for s in systems if s not in SYSTEMS]
    if unknown:
        raise SystemExit(f"unknown systems {unknown}; choose from {sorted(SYSTEMS)}")
    build(Path(args.comparison), args.limit, systems, Path(args.out), args.tag)


if __name__ == "__main__":
    main()
