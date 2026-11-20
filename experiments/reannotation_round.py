"""Prepare and process a full blind re-annotation round for the n=30 writer
replication (210 items).

The previous n=30 sensitivity cohort mixed a pre-registered 12-trajectory
round with an 18-trajectory round added later; stratified reliability showed
that the added round is much weaker (0.786 raw / 0.126 kappa). This round
re-annotates all 30 trajectories from scratch with two independent human
annotators and a human adjudicator. Existing labels are never overwritten.

Workflow:
    python -m experiments.reannotation_round init
    # hand annotator_RA.csv and annotator_RB.csv to two independent people
    python -m experiments.reannotation_round check --a <RA.csv> --b <RB.csv>
    # a human fills adj_* fields in adjudication_sheet.csv
    python -m experiments.reannotation_round merge --sheet <filled.csv>
    python -m experiments.reannotation_round summarize

`init` writes into results/status_drift_v3_replication_writer/
reannotation_2026-11-20/ by default.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from experiments.analyze_replication_n30 import CONDITIONS, outcome, wilson
from experiments.check_v3_annotations import ALLOWED, validate

BASE = Path("results/status_drift_v3_replication_writer")
OLD_COHORTS = [BASE / "annotation_v325", BASE / "annotation_v325_remaining"]
DEFAULT_OUT = BASE / "reannotation_2026-11-20"
GUIDELINES = Path("docs/research/V3_ANNOTATION_GUIDELINES.md")
LABEL_FIELDS = (
    "proposition_identity", "primary_dimension", "status_expressed",
    "expressed_status", "action_status", "evidence_support", "primary_judgment",
    "subtype", "rationale", "confidence", "turn_references",
)
SHEET_FIELDS = ["item_id", "annotator_id", *LABEL_FIELDS,
                "target_proposition", "target_question", "memory_text", "dialogue"]
ADJUDICABLE = (
    "proposition_identity", "primary_dimension", "status_expressed",
    "expressed_status", "action_status", "evidence_support", "primary_judgment",
    "subtype",
)
ADJ_FIELDS = ["item_id", "disputed_fields",
              *(f"A_{field}" for field in LABEL_FIELDS),
              *(f"B_{field}" for field in LABEL_FIELDS),
              *(f"adj_{field}" for field in ADJUDICABLE),
              "adjudicator", "rule",
              "target_proposition", "target_question", "memory_text", "dialogue"]
ADJUDICATION_FIELDS = ["item_id", "trajectory_id", "condition", "dimension",
                       "gold_status", "adjudicator",
                       *(f"{side}_{field}" for field in LABEL_FIELDS for side in ("A", "B")),
                       *(f"adj_{field}" for field in ADJUDICABLE),
                       "adj_confidence", "rule"]
SEED_A = 20261120
SEED_B = 20261121


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_key() -> dict[str, dict]:
    key = {}
    for directory in OLD_COHORTS:
        for row in read_csv(directory / "adjudication.csv"):
            key[row["item_id"]] = {
                "item_id": row["item_id"],
                "trajectory_id": row["trajectory_id"],
                "condition": row["condition"],
                "dimension": row["dimension"],
                "gold_status": row["gold_status"],
            }
    return key


def load_items() -> list[dict]:
    items = {}
    for directory in OLD_COHORTS:
        for row in read_csv(directory / "annotation_items.csv"):
            items[row["item_id"]] = {
                "item_id": row["item_id"],
                "target_proposition": row["target_proposition"],
                "target_question": row["target_question"],
                "memory_text": row["memory_text"],
                "dialogue": row["dialogue"],
            }
    return [items[key] for key in sorted(items)]


def init(out: Path, force: bool = False) -> None:
    existing = out / "annotator_RA.csv"
    if existing.exists() and not force:
        raise SystemExit(f"{out} already contains a frozen round; pass --force to rebuild")
    items = load_items()
    key = load_key()
    assert len(items) == 210, len(items)
    assert len(key) == 210, len(key)
    assert {item["item_id"] for item in items} == set(key)
    assert len({row["trajectory_id"] for row in key.values()}) == 30
    assert len({row["condition"] for row in key.values()}) == 7
    assert Counter(row["condition"] for row in key.values()) == {c: 30 for c in CONDITIONS}

    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "annotation_items.csv", items,
              ["item_id", "target_proposition", "target_question",
               "memory_text", "dialogue"])
    write_csv(out / "key.csv", [key[item["item_id"]] for item in items], list(next(iter(key.values()))))

    for annotator, seed in (("RA", SEED_A), ("RB", SEED_B)):
        order = list(items)
        random.Random(seed).shuffle(order)
        rows = []
        for item in order:
            row = {field: "" for field in SHEET_FIELDS}
            row.update(item)
            row["annotator_id"] = annotator
            rows.append(row)
        write_csv(out / f"annotator_{annotator}.csv", rows, SHEET_FIELDS)

    readme = f"""# n = 30 full re-annotation (2026-11-20)

Two independent human annotators and a human adjudicator re-annotate all
210 items (30 trajectories x 7 conditions). The previous labels stay in
`../annotation_v325/` and `../annotation_v325_remaining/`; nothing here
overwrites them.

## Files

- `annotator_RA.csv`, `annotator_RB.csv` — blind sheets with different row
  orders. Give one to each annotator. They contain no condition, no gold
  status, and no old labels.
- `annotation_items.csv` — the items in canonical id order (reference only;
  annotators should use their own sheet).
- `key.csv` — hidden mapping from item id to trajectory, condition, dimension,
  and gold status. Do not give this to annotators. It is curator-only and is
  intentionally not committed to the repository.
- `frozen_manifest.json` — SHA-256 of the inputs and sheets at freeze time.

## Independence rules

1. Each annotator fills only their own file and does not see the other file,
   the key, the old labels, or condition summaries.
2. Do not discuss items with the other annotator before both files are
   returned. Questions about the rubric go to the coordinator, not to each
   other.
3. Keep `annotator_id` as `RA` / `RB`; do not rename the files.
4. Fill every required field; `rationale` is required for any judgment other
   than `NO_DISTORTION`, and `confidence` is always required.
5. Return the CSVs unchanged in structure.

## Rubric

Use `docs/research/V3_ANNOTATION_GUIDELINES.md` (frozen hash in the manifest).
The primary judgment is one of `NO_DISTORTION`, `LEGITIMATE_UPDATE`,
`UNSUPPORTED_STATUS_DISTORTION`, `STATUS_OMISSION`, `PROPOSITION_LOSS`,
`AMBIGUOUS_UNASSESSABLE`.

## After both sheets return

```
python -m experiments.reannotation_round check --a annotator_RA.csv --b annotator_RB.csv
```

This writes `validation.json`, `agreement.json`, and
`adjudication_sheet.csv` containing only substantively disputed items. A third
human fills the `adj_*` fields for the fields listed in `disputed_fields`,
signs `adjudicator`, and records a short `rule`. `rationale` and
`turn_references` are never adjudicated: the merged file keeps annotator RA's
wording, with RB's wording preserved in the `B_*` columns. Final confidence is
the lower of the two annotators' values. Then:

```
python -m experiments.reannotation_round merge --sheet adjudication_sheet.csv
python -m experiments.reannotation_round summarize
```

`merge` refuses to run while any disputed field is blank. It never resolves a
dispute automatically. `summarize` writes `condition_table.csv`,
`summary.json`, and `reliability.json` for the re-annotated n = 30 cohort.

## 中文要点

- 两名批注者各用一份表，行序不同；互不看对方的表、key、旧标签或条件汇总。
- key.csv 含条件与 gold，只能由协调者保管。
- 两人都交回后再由第三人人工裁决分歧；脚本不会自动替任何一方裁决。
- 旧标签原样保留，重批结果写入本目录。
"""
    (out / "README.md").write_text(readme, encoding="utf-8")

    outputs = [out / "annotation_items.csv", out / "key.csv",
               out / "annotator_RA.csv", out / "annotator_RB.csv",
               out / "README.md"]
    manifest = {
        "status": "awaiting_labels",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "n_items": len(items),
        "n_trajectories": len({row["trajectory_id"] for row in key.values()}),
        "conditions": {c: 30 for c in CONDITIONS},
        "seeds": {"RA": SEED_A, "RB": SEED_B},
        "inputs": [
            {"path": str(GUIDELINES), "sha256": sha256(GUIDELINES)},
            *[{"path": str(directory / name), "sha256": sha256(directory / name)}
              for directory in OLD_COHORTS
              for name in ("annotation_items.csv", "adjudication.csv")],
        ],
        "outputs": [{"path": path.name, "sha256": sha256(path),
                     "curator_only": path.name == "key.csv"} for path in outputs],
    }
    (out / "frozen_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"froze {len(items)} items in {out}")
    print("give annotator_RA.csv and annotator_RB.csv to two independent annotators")


def _load_sheet(path: Path, key: dict[str, dict]) -> list[dict]:
    rows = read_csv(path)
    ids = [row["item_id"] for row in rows]
    if len(rows) != 210 or len(set(ids)) != 210 or set(ids) != set(key):
        raise SystemExit(
            f"{path}: expected 210 unique item ids matching key.csv; got {len(rows)} rows")
    return rows


def check(a_path: Path, b_path: Path, out: Path) -> None:
    key = load_key()
    a_rows = _load_sheet(a_path, key)
    b_rows = _load_sheet(b_path, key)

    validation = {}
    for name, rows in (("RA", a_rows), ("RB", b_rows)):
        report = validate(rows)
        validation[name] = {
            "rows": len(rows),
            "missing_required": sum(value["missing"] for value in report.values()),
            "invalid_values": sum(len(value["invalid"]) for value in report.values()),
            "details": report,
        }

    a_map = {row["item_id"]: row for row in a_rows}
    b_map = {row["item_id"]: row for row in b_rows}
    agreement = {}
    for field in ALLOWED:
        pairs = []
        for item_id in sorted(key):
            left, right = a_map[item_id], b_map[item_id]
            if not (left.get(field) or "").strip() or not (right.get(field) or "").strip():
                continue
            if field == "expressed_status" and (
                    left["primary_dimension"].strip() != right["primary_dimension"].strip()):
                continue
            pairs.append((left[field].strip(), right[field].strip()))
        counts_a = Counter(x for x, _ in pairs)
        counts_b = Counter(y for _, y in pairs)
        confusion: dict[str, dict[str, int]] = {}
        for x, y in pairs:
            confusion.setdefault(x, {})
            confusion[x][y] = confusion[x].get(y, 0) + 1
        from experiments.check_annotations import cohen_kappa
        n = len(pairs)
        agreement[field] = {
            "n_pairs": n,
            "raw_agreement": sum(x == y for x, y in pairs) / n if n else None,
            "cohen_kappa": cohen_kappa([x for x, _ in pairs], [y for _, y in pairs]),
            "label_counts_a": dict(counts_a),
            "label_counts_b": dict(counts_b),
            "confusion_matrix": confusion,
        }

    disputes = []
    for item_id in sorted(key):
        left, right = a_map[item_id], b_map[item_id]
        differing = [field for field in ADJUDICABLE
                     if (left.get(field) or "").strip() != (right.get(field) or "").strip()]
        if differing:
            row = {"item_id": item_id, "disputed_fields": ";".join(differing)}
            for field in LABEL_FIELDS:
                row[f"A_{field}"] = left.get(field, "")
                row[f"B_{field}"] = right.get(field, "")
            for field in ADJUDICABLE:
                row[f"adj_{field}"] = ""
            for field in ("target_proposition", "target_question", "memory_text", "dialogue"):
                row[field] = left[field]
            row["adjudicator"] = ""
            row["rule"] = ""
            disputes.append(row)

    out.mkdir(parents=True, exist_ok=True)
    (out / "validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "agreement.json").write_text(
        json.dumps(agreement, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(out / "adjudication_sheet.csv", disputes, ADJ_FIELDS)

    primary = agreement["primary_judgment"]
    print(f"common items: 210; disputed items: {len(disputes)}")
    print(f"primary judgment: raw {primary['raw_agreement']:.3f}, "
          f"kappa {primary['cohen_kappa']:.3f}")
    print(f"wrote {out / 'adjudication_sheet.csv'}")
    for name, report in validation.items():
        if report["missing_required"] or report["invalid_values"]:
            print(f"{name}: missing={report['missing_required']} "
                  f"invalid={report['invalid_values']} (see validation.json)")
    if any(report["missing_required"] or report["invalid_values"]
           for report in validation.values()):
        raise SystemExit(1)


def merge(sheet_path: Path, out: Path) -> None:
    key = load_key()
    a_rows = _load_sheet(out / "annotator_RA.csv", key)
    b_rows = _load_sheet(out / "annotator_RB.csv", key)
    sheet = {row["item_id"]: row for row in read_csv(sheet_path) if row["item_id"]}

    a_map = {row["item_id"]: row for row in a_rows}
    b_map = {row["item_id"]: row for row in b_rows}
    confidence_rank = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    merged, final_rows, problems = [], [], []
    for item_id in sorted(key):
        left, right = a_map[item_id], b_map[item_id]
        disputed = sheet.get(item_id)
        adj = {}
        for field in LABEL_FIELDS:
            a_value = (left.get(field) or "").strip()
            b_value = (right.get(field) or "").strip()
            if field in ADJUDICABLE:
                if a_value == b_value:
                    adj[field] = a_value
                    continue
                value = (disputed or {}).get(f"adj_{field}", "").strip()
                if not value:
                    problems.append(f"{item_id}:{field} adjudicated value required")
                adj[field] = value
            elif field == "confidence":
                values = [value for value in (a_value, b_value) if value]
                adj[field] = (min(values, key=confidence_rank.get)
                              if values else "")
            else:
                adj[field] = a_value or b_value
        if disputed and not (disputed.get("adjudicator") or "").strip():
            problems.append(f"{item_id}: adjudicator missing")
        row = {
            "item_id": item_id,
            "trajectory_id": key[item_id]["trajectory_id"],
            "condition": key[item_id]["condition"],
            "dimension": key[item_id]["dimension"],
            "gold_status": key[item_id]["gold_status"],
            "adjudicator": (disputed or {}).get("adjudicator", "").strip() or "human-adjudicator",
            "rule": (disputed or {}).get("rule", "").strip() or "agreement",
        }
        for field in LABEL_FIELDS:
            row[f"A_{field}"] = (left.get(field) or "").strip()
            row[f"B_{field}"] = (right.get(field) or "").strip()
        for field in ADJUDICABLE:
            row[f"adj_{field}"] = adj[field]
        row["adj_confidence"] = adj["confidence"]
        merged.append(row)
        final_rows.append(adj | {"item_id": item_id})

    if problems:
        raise SystemExit("merge blocked:\n" + "\n".join(problems[:20]))

    report = validate(final_rows)
    missing = sum(value["missing"] for value in report.values())
    invalid = sum(len(value["invalid"]) for value in report.values())
    if missing or invalid:
        raise SystemExit(f"merged labels invalid: missing={missing} invalid={invalid}; "
                         "see merge_report.json")

    write_csv(out / "adjudication.csv", merged, ADJUDICATION_FIELDS)
    (out / "merge_report.json").write_text(json.dumps({
        "status": "merged",
        "n_items": len(merged),
        "n_disputed_items": len(sheet),
        "missing_required": missing,
        "invalid_values": invalid,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out / 'adjudication.csv'} ({len(merged)} rows, {len(sheet)} disputed)")


def summarize(out: Path) -> None:
    rows = read_csv(out / "adjudication.csv")
    assert len(rows) == 210, len(rows)
    assert len({row["trajectory_id"] for row in rows}) == 30
    by_condition = {condition: [row for row in rows if row["condition"] == condition]
                    for condition in CONDITIONS}
    assert all(len(group) == 30 for group in by_condition.values())

    table = []
    for condition in CONDITIONS:
        group = by_condition[condition]
        values = [outcome(row) for row in group]
        n = len(group)
        faithful = sum(value["faithful"] for value in values)
        loss = sum(value["loss"] for value in values)
        low, high = wilson(faithful, n)
        table.append({
            "condition": condition,
            "n": n,
            "faithful_n": faithful,
            "faithful_rate": faithful / n,
            "joint_fidelity_low": low,
            "joint_fidelity_high": high,
            "omission_n": sum(value["omission"] for value in values),
            "unsupported_n": sum(value["unsupported"] for value in values),
            "ambiguous_n": sum(value["ambiguous"] for value in values),
            "loss_n": loss,
            "preserved_n": n - loss,
            "conditional_status_fidelity": faithful / (n - loss) if n - loss else None,
        })
    write_csv(out / "condition_table.csv", table, list(table[0]))
    summary = {
        "status": "reannotated",
        "n_items": len(rows),
        "judgment": dict(Counter(row["adj_primary_judgment"] for row in rows)),
        "identity": dict(Counter(row["adj_proposition_identity"] for row in rows)),
        "condition_table": table,
        "reliability_source": "agreement.json",
    }
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reliability = json.loads((out / "agreement.json").read_text(encoding="utf-8"))
    (out / "reliability.json").write_text(json.dumps(
        reliability["primary_judgment"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"wrote {out / 'condition_table.csv'} and {out / 'summary.json'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init")
    p_init.add_argument("--force", action="store_true")
    p_check = sub.add_parser("check")
    p_check.add_argument("--a", type=Path, required=True)
    p_check.add_argument("--b", type=Path, required=True)
    p_merge = sub.add_parser("merge")
    p_merge.add_argument("--sheet", type=Path, required=True)
    sub.add_parser("summarize")
    args = parser.parse_args()

    if args.command == "init":
        init(args.out, force=args.force)
    elif args.command == "check":
        check(args.a, args.b, args.out)
    elif args.command == "merge":
        merge(args.sheet, args.out)
    else:
        summarize(args.out)


if __name__ == "__main__":
    main()
