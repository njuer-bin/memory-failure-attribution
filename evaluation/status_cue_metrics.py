"""Deterministic status-cue metrics for epistemic and intentional memories.

This is a heuristic, judge-independent check: does a memory still contain a cue
consistent with the gold status, an opposite cue, both, or neither? It is meant
to quantify status-cue loss separately from proposition retention.

Cue state values:
- MATCH: a gold-consistent cue is present and no opposite cue is present.
- MIXED: both a gold-consistent and an opposite cue are present.
- OPPOSITE: only an opposite cue is present.
- ABSENT: neither is present.
"""
from __future__ import annotations

import json
from pathlib import Path

DEPTHS = ("1", "2", "3", "5")

EPI_CERTAIN_TERMS = ["确认", "不再猜测", "不是猜测"]
EPI_POSSIBLE_TERMS = ["可能", "不确定", "尚未确认", "还没有确认", "还没确认", "不能确定", "未确认"]

INT_COMMITTED_TERMS = ["决定", "承诺", "按计划推进", "已定计划"]
INT_CONSIDERING_TERMS = ["考虑", "未作决定", "没有作出决定", "尚未决定", "还没决定",
                         "未决定", "没有决定"]


def _strip(text: str, terms: list[str]) -> str:
    for term in terms:
        text = text.replace(term, "")
    return text


def cue_state(text: str, dimension: str, gold_status: str) -> str:
    if dimension == "epistemic":
        possible = any(term in text for term in EPI_POSSIBLE_TERMS)
        base = _strip(text, EPI_POSSIBLE_TERMS)
        certain = any(term in base for term in EPI_CERTAIN_TERMS)
        if gold_status == "CERTAIN":
            claim, other = certain, possible
        else:
            claim, other = possible, certain
    elif dimension == "intentional":
        considering = any(term in text for term in INT_CONSIDERING_TERMS)
        base = _strip(text, INT_CONSIDERING_TERMS)
        committed = any(term in base for term in INT_COMMITTED_TERMS)
        if gold_status == "COMMITTED":
            claim, other = committed, considering
        else:
            claim, other = considering, committed
    else:
        return "NA"
    if claim and other:
        return "MIXED"
    if claim:
        return "MATCH"
    if other:
        return "OPPOSITE"
    return "ABSENT"


def summarize_records(records_path: str | Path) -> dict:
    rows = [json.loads(line) for line in open(records_path, encoding="utf-8") if line.strip()]
    conditions = [f"{kind}_d{depth}" for kind in ("direct", "recursive", "rewrite_matched")
                  for depth in DEPTHS]
    summary = {}
    for cond in conditions:
        kind, depth = cond.split("_d")
        counts = {"MATCH": 0, "MIXED": 0, "OPPOSITE": 0, "ABSENT": 0}
        n = 0
        for row in rows:
            if not row.get("has_legitimate_update"):
                continue
            if row["dimension"] not in ("epistemic", "intentional"):
                continue
            memory = (row.get(f"{kind}_memories") or {}).get(depth, "")
            if not memory:
                continue
            n += 1
            counts[cue_state(memory, row["dimension"], row["gold_status"])] += 1
        if n:
            summary[cond] = {"n": n, **counts}
    return summary


def main() -> None:
    import sys
    path = Path(sys.argv[1])
    summary = summarize_records(path / "records.jsonl")
    print(f"{'condition':<22}{'n':<5}{'MATCH':<7}{'MIXED':<7}{'OPPOSITE':<10}{'ABSENT'}")
    for cond, counts in summary.items():
        print(f"{cond:<22}{counts['n']:<5}{counts['MATCH']:<7}{counts['MIXED']:<7}"
              f"{counts['OPPOSITE']:<10}{counts['ABSENT']}")


if __name__ == "__main__":
    main()
