"""Diagnose why a round-2 gate annotation sheet fails inter-annotator agreement.

Reads two filled ``round2_gate_only_annotated*.csv`` sheets and reports marginals,
the pairwise label table, and whether either sheet's ``no`` notes are a mechanical
template (the round-2 failure mode: quoting a token from the reference answer as
"the missing fact"). Emits JSON for the record; no judgement beyond the facts.

Usage:
    python -m experiments.diagnose_gate_annotations \
        --a results/annotation_package/round2_gate_only_annotated1.csv \
        --b results/annotation_package/round2_gate_only_annotated2.csv \
        --out results/analysis_annotations_round2_diagnostic.json
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from evaluation.paired_stats import agreement, cohens_kappa

_TEMPLATE = re.compile(
    r"^Missing fact:\s*(.+?)\s+is not stated in the evidence\.?$", re.I
)


def _load(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {row["sample_id"]: row for row in csv.DictReader(fh)}


def _label(value: str) -> bool | str | None:
    text = (value or "").strip().lower()
    if text in {"yes", "y", "true", "1"}:
        return True
    if text in {"no", "n", "false", "0"}:
        return False
    if text == "uncertain":
        return "UNC"
    return None


def _marginals(rows: dict[str, dict[str, str]]) -> dict[str, int]:
    return dict(Counter(
        (row.get("evidence_sufficient_yes_no_uncertain") or "").strip().lower()
        for row in rows.values()
    ))


def _template_stats(rows: dict[str, dict[str, str]]) -> dict[str, Any]:
    matched = []
    for row in rows.values():
        if (row.get("evidence_sufficient_yes_no_uncertain") or "").strip().lower() != "no":
            continue
        m = _TEMPLATE.match((row.get("notes") or "").strip())
        if not m:
            continue
        token = m.group(1).lower()
        reference = (row.get("reference_answer") or "").lower()
        evidence = (row.get("gold_evidence") or "").lower()
        matched.append({
            "sample_id": row["sample_id"],
            "token": token,
            "token_in_reference": bool(re.search(r"\b" + re.escape(token) + r"\b", reference)),
            "token_in_evidence": bool(re.search(r"\b" + re.escape(token) + r"\b", evidence)),
        })
    return {
        "no_rows": sum(1 for r in rows.values()
                       if (r.get("evidence_sufficient_yes_no_uncertain") or "").strip().lower() == "no"),
        "template_matches": len(matched),
        "token_in_reference": sum(x["token_in_reference"] for x in matched),
        "token_in_evidence": sum(x["token_in_evidence"] for x in matched),
        "top_tokens": Counter(x["token"] for x in matched).most_common(15),
        "examples": matched[:10],
    }


def diagnose(a: dict[str, dict[str, str]], b: dict[str, dict[str, str]]) -> dict[str, Any]:
    pairs: Counter[tuple[Any, Any]] = Counter()
    x_vals, y_vals = [], []
    for sid in sorted(a):
        if sid not in b:
            continue
        x, y = _label(a[sid].get("evidence_sufficient_yes_no_uncertain", "")), _label(
            b[sid].get("evidence_sufficient_yes_no_uncertain", ""))
        pairs[(x, y)] += 1
        if x in (True, False) and y in (True, False):
            x_vals.append(bool(x))
            y_vals.append(bool(y))
    return {
        "n": len(x_vals),
        "agreement": agreement(x_vals, y_vals),
        "kappa": cohens_kappa(x_vals, y_vals),
        "marginals_a": _marginals(a),
        "marginals_b": _marginals(b),
        "pair_table": {
            f"{key[0]}->{key[1]}": n
            for key, n in sorted(pairs.items(), key=lambda kv: str(kv[0]))
        },
        "templates_a": _template_stats(a),
        "templates_b": _template_stats(b),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", required=True)
    parser.add_argument("--b", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    result = diagnose(_load(Path(args.a)), _load(Path(args.b)))
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
