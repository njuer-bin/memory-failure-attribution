"""Re-attribute failures with the human per-fact gate (label-only, no API).

For questions covered by the round-3 annotation package, replace the automatic
evidence-sufficiency gate with the two-annotator consensus gate and recompute
``answer_failure_type`` with the frozen attribution path. Questions outside the
package (or where the annotators disagree on the row gate) keep the stored gate
and are reported as uncovered.

Usage:
    python -m experiments.regate_with_human_gate \
        --comparison results/_corrected_comparison_locomo_n200.jsonl \
        --out results/analysis_regate_locomo_n200.json
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from evaluation import attribution
from experiments.score_fact_annotations import _row_gates

MODES_ORDER = ("real_memory", "oracle_memory", "oracle_context")


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def consensus_gates(key_path: Path, sheet_paths: list[Path]) -> tuple[dict[str, str], dict[str, str]]:
    """Return ({sample_id: gate}, {sample_id: question_id}) for agreed rows."""
    key = _load_csv(key_path)
    annotations = [{row["fact_id"]: row for row in _load_csv(p)} for p in sheet_paths]
    gates = [_row_gates(key, labels, uncertain_as_insufficient=True) for labels in annotations]
    agreed: dict[str, str] = {}
    for sid, ga in gates[0].items():
        gb = gates[1].get(sid)
        if ga == gb and ga in ("sufficient", "insufficient"):
            agreed[sid] = ga
    qid = {row["sample_id"]: row.get("question_id", "") for row in key}
    return agreed, qid


def regate(
    comparison: Path,
    sample_gate: dict[str, str],
    sample_qid: dict[str, str],
) -> dict[str, Any]:
    by_qid = {qid: gate for sid, gate in sample_gate.items() if (qid := sample_qid.get(sid))}
    transitions: dict[str, Counter] = defaultdict(Counter)
    covered = 0
    uncovered = 0
    rows = [json.loads(line) for line in comparison.read_text(encoding="utf-8").splitlines() if line.strip()]
    for row in rows:
        gate_status = by_qid.get(str(row.get("question_id")))
        use_human = gate_status is not None
        if use_human:
            covered += 1
        else:
            uncovered += 1
        gold = row.get("gold_evidence") or []
        for mode, mode_data in row.get("modes", {}).items():
            answer = mode_data.get("answer") or {}
            old = mode_data.get("answer_failure_type")
            if use_human:
                gate = {
                    "status": gate_status,
                    "evidence_sufficient": gate_status == "sufficient",
                    "confidence": "high",
                    "reason": "round-3 per-fact human consensus",
                    "adjudication": "human_fact_consensus",
                }
                new = attribution.attribute_failure(answer, gate, mode_data, gold, mode=mode)
            else:
                new = old
            transitions[mode][f"{old}->{new}"] += 1
    result: dict[str, Any] = {
        "comparison": str(comparison),
        "questions_covered_by_human_gate": covered,
        "questions_uncovered": uncovered,
        "per_mode": {},
    }
    for mode in sorted(transitions):
        old_dist = Counter()
        new_dist = Counter()
        changed = 0
        for trans, count in transitions[mode].items():
            old, new = trans.split("->")
            old_dist[old] += count
            new_dist[new] += count
            if old != new:
                changed += count
        result["per_mode"][mode] = {
            "old_failure_distribution": dict(sorted(old_dist.items())),
            "new_failure_distribution": dict(sorted(new_dist.items())),
            "e0_old": old_dist.get("E0_EVIDENCE_INSUFFICIENT", 0),
            "e0_new": new_dist.get("E0_EVIDENCE_INSUFFICIENT", 0),
            "changed": changed,
            "transitions": dict(sorted(transitions[mode].items())),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", required=True)
    parser.add_argument("--key", default="results/annotation_package/round3_key.csv")
    parser.add_argument("--sheet", action="append", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    gates, qid = consensus_gates(Path(args.key), [Path(p) for p in args.sheet])
    result = regate(Path(args.comparison), gates, qid)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
