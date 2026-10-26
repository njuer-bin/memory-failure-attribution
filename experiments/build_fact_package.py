"""Build the round-3 per-fact gate annotation package.

The reference answer of each row is decomposed once, here, into atomic facts
(``experiments/fact_specs.py``). Annotators do not decompose; they only mark,
for each fact, whether the listed gold evidence states it. This removes the
gestalt judgement that made round 2's gate field unreliable.

Outputs under ``results/annotation_package``:

- ``round3_fact_presence.csv`` — one row per fact, blinded (no stored verdict,
  no adjudicated label, no model answer);
- ``round3_key.csv`` — hidden fact metadata plus stored and adjudicated gate
  labels, for scoring only;
- ``README_round3.md`` — instructions and the pre-registered acceptance bar.

Usage:
    python -m experiments.build_fact_package
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from experiments.fact_specs import FACT_SPECS


def _load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


README = """# Round 3 — per-fact evidence-sufficiency annotation

Round 1's gate field was gestalt and failed (kappa 0.0). Round 2 asked for the
same gestalt judgement with a tighter checklist and also failed (kappa 0.18).
Round 3 changes the task shape: each reference answer has been decomposed into
its atomic facts, and you only answer one binary question per fact.

## What you fill in

`round3_fact_presence.csv` has one row per atomic fact. Fill only
`fact_present_yes_no_uncertain` and, when not `yes`, `notes`.

For each row, using only that row's `question`, `gold_evidence` and
`fact_text`:

- `yes` — the gold evidence states the fact, or the fact follows from it by
  trivial arithmetic/date arithmetic (e.g. two evidence dates 4 days apart for
  a fact "4 days passed").
- `no` — the gold evidence does not state the fact.
- `uncertain` — the evidence contains the needed facts but a relative time
  expression ("last Friday", "a few years ago") cannot be resolved because the
  row carries no usable date. Add a note naming the unresolvable phrase.

Paraphrase is fine: the fact need not appear word-for-word. Only the
proposition matters. A fact phrased in the negative ("the evidence does not
mention X") is `yes` when the evidence indeed never mentions X.

Do not read `round3_key.csv`. Work independently. Every `no` gets a one-line
note naming the absent proposition; every `uncertain` gets a note naming the
unresolvable phrase.

## Worked examples

`yes` (explicit):
- `longmemeval-006`, fact "The narrator has met up with Alex from Germany
  twice." The evidence says "a friend Alex from there ... we've met up twice
  already". `yes`.

`yes` (different wording, same proposition):
- `locomo-036`, fact "Melanie plays the violin." The evidence says "playing my
  violin". `yes`.

`no` (one asserted item absent):
- `locomo-038`, fact "Melanie has a dog." The evidence names cats (Bailey,
  Oliver, Oscar) but never a dog. `no` — note "no dog".

`no` (the fact's content is never stated):
- `locomo-021`, fact "Melanie saw a sign at the cafe stating that someone is not
  able to leave." The evidence mentions "thoughtful signs like this" but never
  what any sign says. `no` — note "sign content absent".

`uncertain` (relative time with no anchor):
- A fact "Gina got her tattoo a few years ago" where the evidence says only
  "a few years ago" and carries no date. `uncertain` — note the phrase.
  If the evidence gives a date that makes the phrase resolvable, mark `yes`.

## Scoring (pre-registered)

Two independent annotators. The instrument is accepted only if **both** clear:

1. **fact-level kappa >= 0.6** on `fact_present_yes_no_uncertain`;
2. **row-level kappa >= 0.6** after aggregating facts to a row gate
   (any required fact absent -> insufficient; an any-of group passes if at
   least one alternative is present).

How `uncertain` is scored: fact-level kappa uses only rows both annotators
decided yes/no. At row level, a required fact marked `uncertain` counts as
absent in the **primary** gate, because an unresolvable relative date means the
reference answer is not derivable from the listed evidence — the gate's
definition of insufficient. The same rows are also scored with `uncertain`
excluded, as a sensitivity analysis; both are reported.

If accepted, the aggregated row gate is compared with the 200 adjudicated human
labels (round 1) and replaces the automatic gate wherever E0 is reported.

Scope note: facts describe the answer to the question, not incidental
elaboration in the reference. For a counting question the count is the fact;
the enumerated items are not re-checked unless the question asks for them.
"""


def build(rows: list[dict[str, str]], adjudicated: dict[str, dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    fact_rows: list[dict[str, str]] = []
    key_rows: list[dict[str, str]] = []
    missing = [r["sample_id"] for r in rows if r["sample_id"] not in FACT_SPECS]
    extra = [sid for sid in FACT_SPECS if sid not in {r["sample_id"] for r in rows}]
    if missing or extra:
        raise SystemExit(f"fact spec mismatch: missing={missing[:5]} extra={extra[:5]}")
    for row in rows:
        sid = row["sample_id"]
        adjudged = adjudicated.get(sid, {})
        for i, (text, group) in enumerate(FACT_SPECS[sid], start=1):
            fact_id = f"{sid}-f{i}"
            group_id = f"{sid}:{group}" if group else ""
            fact_rows.append({
                "sample_id": sid,
                "fact_id": fact_id,
                "fact_text": text,
                "question": row["question"],
                "reference_answer": row["reference_answer"],
                "gold_evidence": row["gold_evidence"],
                "fact_present_yes_no_uncertain": "",
                "notes": "",
            })
            key_rows.append({
                "sample_id": sid,
                "fact_id": fact_id,
                "group": group_id,
                "question_id": adjudged.get("question_id", ""),
                "benchmark": sid.split("-")[0],
                "fact_text": text,
                "stored_gate": adjudged.get("stored_gate", ""),
                "adjudicated_gate": adjudged.get("adj_evidence_sufficient", ""),
            })
    return fact_rows, key_rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", default="results/annotation_package/round2_gate_only.csv")
    parser.add_argument("--adjudicated", default="results/annotation_package/adjudicated.csv")
    parser.add_argument("--out", default="results/annotation_package")
    args = parser.parse_args()

    rows = _load(Path(args.rows))
    adjudicated = {r["sample_id"]: r for r in _load(Path(args.adjudicated))}
    # question_id comes from the hidden key, used only for provenance.
    key_lookup = {r["sample_id"]: r for r in _load(Path(args.out) / "key.csv")}
    for row in rows:
        extra = key_lookup.get(row["sample_id"], {})
        adjudicated.setdefault(row["sample_id"], {}).update(
            {"question_id": extra.get("question_id", ""),
             "stored_gate": extra.get("gate_status", "")}
        )

    fact_rows, key_rows = build(rows, adjudicated)
    out = Path(args.out)
    with (out / "round3_fact_presence.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(fact_rows[0]))
        writer.writeheader()
        writer.writerows(fact_rows)
    with (out / "round3_key.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(key_rows[0]))
        writer.writeheader()
        writer.writerows(key_rows)
    (out / "README_round3.md").write_text(README, encoding="utf-8")
    print(f"wrote {len(fact_rows)} fact rows for {len(rows)} questions to {out}")


if __name__ == "__main__":
    main()
