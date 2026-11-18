"""Build the Stage 2 60-item calibration candidate sheet.

Composition: 30 LoCoMo intentional candidates, 15 conditional candidates
(LoCoMo + longmemeval_s), and 15 longmemeval_s candidates. Items already used
in the 50-item screening set are excluded by exact candidate key. Because the
LoCoMo-Refined public split contains only 10 conversations and all were used in
the screening set, the LoCoMo arm reuses conversations but not items; the
summary and README record this deviation.

The sheet carries raw dialogue fields only. Gold fields are blank; the proposed
stratum and boundary/cue flags live in the key outside the repository.

Usage:
    G:/aconda/python.exe -m experiments.make_stage2_calibration_set
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from experiments.v3_real_feasibility_audit import (
    EPI_ADVICE,
    PAST_EVAL,
    VAGUE,
    dedupe,
    scan_lme,
    split_sentences,
)

SEED = 20261118
CUE_MISMATCH = re.compile(
    r"\bi think i(?:'ll| will| am going to|'m going to)\b|"
    r"\bi'll definitely\b|\bdefinitely i'll\b|\bmaybe i'll\b", re.I)
COMMITTED = re.compile(
    r"\b(decided|booked|signed up|registered|paid|started|completed|"
    r"committed|going to|will)\b", re.I)
CONSIDERING = re.compile(
    r"\b(thinking|considering|might|maybe|wondering|want to|hope to|"
    r"planning|plan to|intend|leaning toward)\b", re.I)
PREFERENCE = re.compile(
    r"\b(i'm open to|as long as|prefer|would rather|i'd like)\b", re.I)

GOLD_FIELDS = [
    "target_proposition", "gold_dimension", "gold_status",
    "gold_condition_state", "gold_action_state", "gold_strength",
    "gold_confidence", "evidence_quote", "update_history", "notes",
]
CONTENT_FIELDS = [
    "dataset", "source_id", "session_index", "date", "speaker",
    "target_sentence", "context", "later_mention",
]


def key_of(row: dict) -> tuple[str, str, str, str]:
    return (row["dataset"], row["source_id"], str(row["session_index"]),
            re.sub(r"[^a-z0-9 ]", "", row["target_sentence"].lower()))


def flags(row: dict) -> tuple[bool, bool, str]:
    text = row["target_sentence"]
    cue = bool(CUE_MISMATCH.search(text))
    boundary = bool(PAST_EVAL.search(text) or EPI_ADVICE.search(text)
                    or VAGUE.search(text) or PREFERENCE.search(text))
    if len([d for d in row["dimensions"].split(",") if d]) > 1:
        boundary = True
    if COMMITTED.search(text) and CONSIDERING.search(text):
        boundary = True
        proposed = "MIXED"
    elif COMMITTED.search(text):
        proposed = "COMMITTED_COMPLETED"
    elif CONSIDERING.search(text):
        proposed = "CONSIDERING_INTENDING"
    else:
        proposed = "OTHER"
    return cue, boundary, proposed


def load_pool(args: argparse.Namespace) -> tuple[list[dict], list[dict]]:
    with Path(args.candidates).open(encoding="utf-8-sig") as handle:
        oracle_rows = list(csv.DictReader(handle))
    s_rows = scan_lme(Path(args.lme_s))
    for row in s_rows:
        row["candidate_id"] = ""
    return dedupe(oracle_rows + s_rows), oracle_rows + s_rows


def screening_keys(path: Path) -> set[tuple[str, str, str, str]]:
    with path.open(encoding="utf-8-sig") as handle:
        return {key_of(row) for row in csv.DictReader(handle)}


def pick(pool: list[dict], n: int, rng: random.Random,
         max_per_source: int, used: set[str]) -> list[dict]:
    by_source: Counter = Counter()
    out = []
    shuffled = pool[:]
    rng.shuffle(shuffled)
    for row in shuffled:
        if len(out) >= n:
            break
        source = (row["dataset"], row["source_id"])
        if by_source[source] >= max_per_source or key_of(row) in used:
            continue
        by_source[source] += 1
        used.add(key_of(row))
        out.append(row)
    return out


def ensure_flags(chosen: list[dict], reserve: list[dict], flag_index: int,
                 minimum: int, used: set[str]) -> None:
    current = sum(1 for row in chosen if row["_flags"][flag_index])
    if current >= minimum:
        return
    for row in reserve:
        if current >= minimum:
            break
        if not row["_flags"][flag_index] or key_of(row) in used:
            continue
        # Replace a non-flagged, non-boundary item from the same dataset.
        for i, existing in enumerate(chosen):
            if (existing["dataset"] == row["dataset"]
                    and not existing["_flags"][flag_index]
                    and not existing["_flags"][1]):
                used.discard(key_of(existing))
                used.add(key_of(row))
                chosen[i] = row
                current += 1
                break


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates",
                        default="results/status_drift_v3_real_audit/candidates.csv")
    parser.add_argument("--lme-s", default="longmemeval_s_sample10.json")
    parser.add_argument("--screening",
                        default="results/status_drift_v3_real_audit/screening_50.csv")
    parser.add_argument("--exclude-sheets", nargs="*", default=[],
                        help="Additional completed sheets whose items must be excluded.")
    parser.add_argument("--out-dir",
                        default="results/status_drift_v3_real_audit/stage2_calibration_60")
    parser.add_argument("--key",
                        default="G:/memory_failure_backup/stage2_calibration_key_2026-11-18.csv")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--profile", choices=["full", "intent_epi"], default="full",
                        help="full = 30 intentional + 15 conditional + 15 LME-s; "
                             "intent_epi = 30 intentional + 10 epistemic, no conditional.")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    pool, raw = load_pool(args)
    excluded = screening_keys(Path(args.screening))
    for sheet in args.exclude_sheets:
        excluded |= screening_keys(Path(sheet))
    pool = [row for row in pool if key_of(row) not in excluded]
    for row in pool:
        row["_flags"] = flags(row)

    locomo_intentional = [r for r in pool if r["dataset"] == "locomo"
                          and r["primary_dimension"] == "intentional"]
    locomo_conditional = [r for r in pool if r["dataset"] == "locomo"
                          and r["primary_dimension"] == "conditional"]
    lme = [r for r in pool if r["dataset"] == "longmemeval"]
    # scan_lme rows have no candidate_id; oracle rows carry C#### ids.
    lme_s = [r for r in lme if r.get("candidate_id", "") == ""]

    used: set[tuple[str, str, str, str]] = set()
    chosen = []
    target_total = 60
    if args.profile == "intent_epi":
        target_total = 40
        # 30 intentional (20 LoCoMo + 10 longmemeval_s), 10 epistemic.
        chosen += pick(locomo_intentional, 20, rng, max_per_source=3, used=used)
        chosen += pick([r for r in lme_s if r["primary_dimension"] == "intentional"],
                       10, rng, max_per_source=2, used=used)
        chosen += pick([r for r in pool if r["dataset"] == "locomo"
                        and r["primary_dimension"] == "epistemic"],
                       5, rng, max_per_source=1, used=used)
        chosen += pick([r for r in lme_s if r["primary_dimension"] == "epistemic"],
                       5, rng, max_per_source=1, used=used)
    else:
        # 30 LoCoMo intentional: 15 proposed considering/intending, 15 committed.
        for stratum, n in (("CONSIDERING_INTENDING", 15), ("COMMITTED_COMPLETED", 15)):
            sub = [r for r in locomo_intentional
                   if r["_flags"][2] == stratum or r["_flags"][2] == "MIXED"]
            chosen += pick(sub, n, rng, max_per_source=4, used=used)
        # 15 conditional: LoCoMo, longmemeval_s, then longmemeval oracle to fill.
        chosen += pick(locomo_conditional, 5, rng, max_per_source=1, used=used)
        chosen += pick([r for r in lme_s if r["primary_dimension"] == "conditional"],
                       5, rng, max_per_source=2, used=used)
        lme_oracle = [r for r in lme if r.get("candidate_id", "")]
        chosen += pick([r for r in lme_oracle
                        if r["primary_dimension"] == "conditional"],
                       5, rng, max_per_source=1, used=used)
        # 15 longmemeval_s.
        chosen += pick(lme_s, 15, rng, max_per_source=3, used=used)

    # Boundary and cue-mismatch anchors (within the selected set).
    reserve = [r for r in pool if key_of(r) not in used]
    boundary_min = 10 if target_total == 60 else 7
    cue_min = 5 if target_total == 60 else 4
    ensure_flags(chosen, reserve, 1, boundary_min, used)
    ensure_flags(chosen, reserve, 0, cue_min, used)

    # Deduplicate and trim/pad to the profile target.
    seen, final = set(), []
    for row in chosen:
        key = key_of(row)
        if key in seen:
            continue
        seen.add(key)
        final.append(row)
    if len(final) > target_total:
        final = final[:target_total]
    if len(final) < target_total:
        for row in reserve:
            if len(final) >= target_total:
                break
            if key_of(row) not in seen:
                seen.add(key_of(row))
                final.append(row)

    rng.shuffle(final)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    columns = ["item_id"] + CONTENT_FIELDS + GOLD_FIELDS
    rows, key_rows = [], []
    prefix = "S2IE" if args.profile == "intent_epi" else "S2C"
    for i, row in enumerate(final, 1):
        item_id = f"{prefix}-{i:03d}"
        record = {"item_id": item_id, **{k: row[k] for k in CONTENT_FIELDS}}
        for field in GOLD_FIELDS:
            record[field] = ""
        rows.append(record)
        key_rows.append({
            "item_id": item_id, "candidate_id": row.get("candidate_id", ""),
            "dataset": row["dataset"], "source_id": row["source_id"],
            "session_index": row["session_index"],
            "target_sentence": row["target_sentence"],
            "proposed_stratum": row["_flags"][2],
            "boundary_flag": int(row["_flags"][1]),
            "cue_mismatch_flag": int(row["_flags"][0]),
        })
    for name in ("sheet.csv", "annotator_A.csv", "annotator_B.csv"):
        with (out / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
    key_path = Path(args.key)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    with key_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(key_rows[0]))
        writer.writeheader()
        writer.writerows(key_rows)

    summary = {
        "profile": args.profile,
        "items": len(rows),
        "datasets": dict(Counter(row["dataset"] for row in final)),
        "auto_primary_dimension": dict(Counter(row["primary_dimension"] for row in final)),
        "proposed_stratum": dict(Counter(row["_flags"][2] for row in final)),
        "boundary_items": sum(1 for row in final if row["_flags"][1]),
        "cue_mismatch_items": sum(1 for row in final if row["_flags"][0]),
        "screening_overlap_excluded": len(excluded),
        "lo_como_conversations_available": 10,
        "lo_como_conversations_used_in_screening": 10,
        "caveat": (
            "The LoCoMo-Refined public split has only 10 conversations and all "
            "were used in the 50-item screening set. This calibration set "
            "excludes the exact screening items but reuses the conversations; "
            "agreement may be mildly inflated. longmemeval_s items are from 10 "
            "instances not used in screening. Proposed strata and flags are "
            "heuristic and live only in the key, not in the annotator sheet."),
    }
    (out / "analysis").mkdir(exist_ok=True)
    (out / "analysis" / "selection_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
