"""Build a blank two-annotator calibration sheet for real-dialogue v2.5.

Selection is restricted to LongMemEval candidates whose source conversation has
not appeared in any earlier screening, calibration, or LSF/SSF sheet. One
candidate is drawn per source conversation so the 40 items are not clustered.

No annotation fields are prefilled: the sheet contains source text and blank
columns only. The two annotators must label independently before adjudication.

Run:
    G:/aconda/python.exe -m experiments.v3_real_calibration_v25_frame
"""

from __future__ import annotations

import csv
import glob
import json
import random
from collections import defaultdict
from pathlib import Path

SEED = 20261118
N_ITEMS = 40
N_UPDATE = 10
AUDIT_DIR = Path("results/status_drift_v3_real_audit")
OUT_DIR = AUDIT_DIR / "calibration_v25_blank"

ANNOTATION_FIELDS = [
    "target_proposition", "action_predicate", "key_arguments",
    "identity", "gold_dimension", "gold_status", "gold_condition_state",
    "gold_action_state", "gold_strength", "outcome", "evidence_quote",
    "confidence", "eligible", "notes",
]


def used_sources() -> set[tuple[str, str]]:
    used = set()
    for path in glob.glob(str(AUDIT_DIR / "**" / "*.csv"), recursive=True):
        if path.endswith("candidates.csv"):
            continue
        with open(path, encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("source_id"):
                    used.add((row.get("dataset", "longmemeval"), row["source_id"]))
    return used


def main() -> None:
    rows = list(csv.DictReader((AUDIT_DIR / "candidates.csv").open(encoding="utf-8")))
    used = used_sources()
    pool = [r for r in rows
            if r["dataset"] == "longmemeval"
            and r["primary_dimension"] == "intentional"
            and ("longmemeval", r["source_id"]) not in used
            and 40 <= len(r["target_sentence"]) <= 300
            and len(r["context"]) >= 200]

    by_source: dict[str, list[dict]] = defaultdict(list)
    for row in pool:
        by_source[row["source_id"]].append(row)

    rng = random.Random(SEED)
    update_sources = sorted(s for s, rs in by_source.items()
                            if any(r["potential_update"] == "yes" for r in rs))
    stable_sources = sorted(s for s in by_source if s not in set(update_sources))
    rng.shuffle(update_sources)
    rng.shuffle(stable_sources)
    chosen_sources = update_sources[:N_UPDATE] + stable_sources[:N_ITEMS - N_UPDATE]
    chosen_sources = sorted(chosen_sources)

    items = []
    for index, source in enumerate(chosen_sources, 1):
        candidates = sorted(by_source[source], key=lambda r: r["candidate_id"])
        item = rng.choice(candidates)
        items.append({
            "item_id": f"RC25-{index:03d}",
            "dataset": item["dataset"],
            "source_id": item["source_id"],
            "session_index": item["session_index"],
            "date": item["date"],
            "speaker": item["speaker"],
            "target_sentence": item["target_sentence"],
            "context": item["context"],
            "candidate_id": item["candidate_id"],
            **{field: "" for field in ANNOTATION_FIELDS},
        })
    rng.shuffle(items)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = list(items[0].keys())
    with (OUT_DIR / "calibration_sheet_blank.csv").open(
            "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(items)

    manifest = {
        "protocol": "real_v25_blank_calibration",
        "seed": SEED,
        "n_items": len(items),
        "n_update_sources_targeted": N_UPDATE,
        "n_update_sources_selected": sum(
            1 for s in chosen_sources
            if any(r["potential_update"] == "yes" for r in by_source[s])),
        "n_sources_available": len(by_source),
        "n_used_sources_excluded": len(used),
        "eligible_pool": len(pool),
        "selection_rule": (
            "LongMemEval only; intentional primary dimension; source conversation "
            "not used in any earlier audit CSV; one candidate per source; "
            "target sentence 40-300 chars; context >= 200 chars; 10 update "
            "sources targeted."),
        "annotation_fields": ANNOTATION_FIELDS,
        "prefilled_labels": False,
        "rule_document": "docs/research/V3_REAL_PROPOSITION_IDENTITY_V25.md",
    }
    (OUT_DIR / "sampling_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
