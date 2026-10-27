"""Build a blinded human-annotation package from oracle runs.

The evaluator is an instrument, not an oracle. This script samples 100–200
records per benchmark, stratified over stored answer verdict, evidence-gate
status and failure type, and writes:

- ``annotations.csv`` — question, reference answer, gold evidence, model
  answer, and empty evidence-sufficiency / answer-correctness fields;
- ``key.csv`` — the hidden sample id map with stored verdicts (never shown to
  annotators);
- ``README.md`` — instructions and the adjudication rule.

Two annotators should label independently; disagreements are adjudicated by a
third pass. Inter-annotator agreement and evaluator precision/recall/F1 are
computed by ``experiments/score_annotations.py``.

Usage:
    python -m experiments.build_annotation_package \
        --run longmemeval=results/oracle_experiments_longmemeval_n200/comparison.jsonl \
        --run locomo=results/oracle_experiments_locomo_n200/comparison.jsonl \
        --per-run 100 --out results/annotation_package
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


def _load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _mode(row: dict[str, Any]) -> dict[str, Any]:
    return (row.get("modes") or {}).get("real_memory") or {}


def _gold_text(row: dict[str, Any]) -> str:
    parts = []
    for i, item in enumerate(row.get("gold_evidence") or []):
        text = str(item.get("text") or "").strip()
        if text:
            parts.append(f"[{i + 1}] {text}")
    return "\n".join(parts)


def _stratum(row: dict[str, Any]) -> str:
    mode = _mode(row)
    verdict = mode.get("answer") or {}
    correct = verdict.get("semantic_correct")
    label = "correct" if correct is True else ("incorrect" if correct is False else "unjudged")
    gate = ((mode.get("evidence_sufficiency") or {}).get("status")) or "unknown"
    return f"{label}|{gate}"


def stratified_sample(rows: list[dict[str, Any]], n: int, rng: random.Random) -> list[dict[str, Any]]:
    usable = [r for r in rows if _gold_text(r) and (_mode(r).get("answer") or {}).get("answer")]
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in usable:
        groups[_stratum(row)].append(row)
    for bucket in groups.values():
        rng.shuffle(bucket)
    # Round-robin over strata so every stratum is represented before any is
    # exhausted; deterministic given the seed.
    order = sorted(groups)
    selected: list[dict[str, Any]] = []
    while len(selected) < n and any(groups[key] for key in order):
        for key in order:
            if groups[key] and len(selected) < n:
                selected.append(groups[key].pop())
    rng.shuffle(selected)
    return selected


def build(run: str, rows: list[dict[str, Any]], n: int, rng: random.Random) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    annotations: list[dict[str, str]] = []
    key: list[dict[str, str]] = []
    for i, row in enumerate(stratified_sample(rows, n, rng)):
        sample_id = f"{run}-{i + 1:03d}"
        mode = _mode(row)
        answer = mode.get("answer") or {}
        annotations.append({
            "sample_id": sample_id,
            "benchmark": run,
            "question": str(row.get("question") or ""),
            "reference_answer": str(row.get("gold_answer") or ""),
            "gold_evidence": _gold_text(row),
            "model_answer": str(answer.get("answer") or ""),
            "evidence_sufficient_yes_no_uncertain": "",
            "answer_correct_yes_no_uncertain": "",
            "notes": "",
        })
        key.append({
            "sample_id": sample_id,
            "question_id": str(row.get("question_id")),
            "stored_semantic_correct": str(answer.get("semantic_correct")),
            "stored_judge_correct": str(answer.get("semantic_judge_correct")),
            "stored_failure_type": str(mode.get("answer_failure_type") or ""),
            "gate_status": str((mode.get("evidence_sufficiency") or {}).get("status") or ""),
            "stratum": _stratum(row),
        })
    return annotations, key


README = """# Blind annotation package

Label each row in `annotations.csv` independently. Do not open `key.csv`.

## Fields

- `evidence_sufficient_yes_no_uncertain`: do the listed gold evidence snippets
  contain enough information to answer the question and justify the reference
  answer? Judge the evidence against the reference answer, not against the
  model answer.
- `answer_correct_yes_no_uncertain`: is `model_answer` correct given the
  reference answer? Accept paraphrases, dates written differently but
  equivalent, and units stated equivalently. Mark `uncertain` when the model
  answer is ambiguous (e.g. names both an old and a new value).
- `notes`: optional, one short line (why uncertain, what is missing).

## Rules

1. Use only the row's own question, reference answer, gold evidence and model
   answer. Do not consult the benchmark or any external source.
2. Evidence sufficiency and answer correctness are independent: an answer can
   be correct by luck while the evidence is insufficient, and vice versa.
3. Temporal wording ("yesterday", "last Saturday", "last week") must be
   resolved against the dates in the evidence when present. If no date makes
   the expression resolvable, mark uncertain and note it.
4. Two annotators label independently. A third pass adjudicates disagreements.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", required=True,
                        help="name=path/to/comparison.jsonl (repeatable)")
    parser.add_argument("--per-run", type=int, default=100)
    parser.add_argument("--out", default="results/annotation_package")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    annotations: list[dict[str, str]] = []
    key: list[dict[str, str]] = []
    for spec in args.run:
        name, path = spec.split("=", 1)
        run_annotations, run_key = build(name, _load(Path(path)), args.per_run, rng)
        annotations.extend(run_annotations)
        key.extend(run_key)

    with (out / "annotations.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(annotations[0]))
        writer.writeheader()
        writer.writerows(annotations)
    with (out / "key.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(key[0]))
        writer.writeheader()
        writer.writerows(key)
    (out / "README.md").write_text(README, encoding="utf-8")
    print(f"wrote {len(annotations)} annotation rows to {out}")


if __name__ == "__main__":
    main()
