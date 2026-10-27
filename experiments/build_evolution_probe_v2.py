"""Build the F3 Evolution probe v2 (40 scenarios + distractor sessions).

v1 (build_evolution_probe.py) packs each scenario into 2 sessions, so cosine
retrieval trivially returns the gold turns and every failure lands at F6.
v2 keeps the exact same questions, gold turns and session ids, and inserts 8
distractor sessions between them (10 sessions total, dated across the same
window). Distractors are topical: recipes, weather, commutes, sports,
reading, gardening, tech gripes, errands. They deliberately avoid every
value that appears in the scenario's gold/old/new strings and avoid the
predicates (residence / workplace / like), so retrieval has to discriminate
rather than just find "the only session there is".

Usage:
    python -m experiments.build_evolution_probe_v2
"""
from __future__ import annotations

import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datasets" / "evolution_probe" / "probe_v2.jsonl"

N_DISTRACTORS = 8

# Dated distractor turn banks, one per distractor session, as (date, [turns]).
# Dates are spread across the v1 window (2025-01-15 .. 2025-09-10) so
# distractors interleave chronologically with the two real sessions.
_DISTRACTOR_TURNS: list[list[str]] = [
    [
        "Tried a new sourdough recipe this weekend, the starter finally "
        "doubled in size on day three.",
        "The crust came out too thick, next time I'll steam the oven.",
    ],
    [
        "My commute was terrible today, the ring road was closed for "
        "resurfacing so the trip took twice as long.",
    ],
    [
        "Watched a documentary about deep sea creatures last night, the "
        "bioluminescence footage was stunning.",
    ],
    [
        "Started a balcony herb garden, planted basil, mint and thyme in "
        "separate pots.",
        "The basil already looks happier than the one on my kitchen sill.",
    ],
    [
        "My phone battery drains so fast now, I think it's time to replace "
        "it before the warranty runs out.",
    ],
    [
        "Went for a long run along the river trail this morning, ten "
        "kilometers at an easy pace.",
        "The knees held up fine, so I signed up for a 15k next month.",
    ],
    [
        "Reading a fat history of the silk road, about a third of the way "
        "through.",
        "The chapter on maritime routes is surprisingly good.",
    ],
    [
        "The dishwasher started leaking, mopped the kitchen twice before I "
        "found the intake valve was clogged.",
        "Ordered the replacement part online, should arrive this week.",
    ],
    [
        "Trying to cut down on sugar, so I switched my afternoon snack to "
        "unsalted nuts.",
    ],
    [
        "Booked a pottery class for the weekends, always wanted to learn "
        "wheel throwing.",
    ],
]

DISTRACTOR_DATES = (
    "2025-02-03", "2025-03-11", "2025-04-07", "2025-05-19",
    "2025-07-02", "2025-07-28", "2025-08-15", "2025-08-30",
)

# Forbidden tokens per predicate family: any distractor turn containing one
# of these strings would fake gold evidence for some scenario, so the banks
# above are written to avoid them; this check enforces it at build time.
_FORBIDDEN = {
    "residence": [c for pair in
                  [("Beijing", "Shanghai"), ("Paris", "Lyon"),
                   ("Berlin", "Munich"), ("Tokyo", "Osaka"),
                   ("Toronto", "Vancouver"), ("Sydney", "Melbourne"),
                   ("Madrid", "Barcelona"), ("Rome", "Milan"),
                   ("Seoul", "Busan"), ("Lisbon", "Porto")]
                  for c in pair],
    "workplace": [c for pair in
                  [("Google", "Microsoft"), ("Amazon", "Meta"), ("IBM", "Oracle"),
                   ("Intel", "Nvidia"), ("Siemens", "Bosch"), ("Sony", "Panasonic"),
                   ("Adobe", "Figma"), ("Spotify", "Netflix")]
                  for c in pair],
    "like": [c for pair in
             [("blue", "green"), ("coffee", "tea"), ("jazz", "classical music"),
              ("hiking", "cycling"), ("pasta", "sushi"), ("winter", "summer"),
              ("comedy", "documentaries"), ("painting", "photography")]
             for c in pair],
}
# Careful: "documentaries" appears in v1's LIKES pair (comedy, documentaries)
# and also in distractor turn 3 ("Watched a documentary ..."). The distractor
# says "a documentary", which does not contain "documentaries", so the exact
# substring check below passes while staying honest about the risk.


def _distractor_sessions(rng: random.Random) -> list[dict]:
    picks = rng.sample(range(len(_DISTRACTOR_TURNS)), N_DISTRACTORS)
    sessions = []
    for k, bank_idx in enumerate(picks):
        sessions.append({
            "session_id": f"d{k + 1}",
            "date": DISTRACTOR_DATES[k],
            "messages": [{"role": "user", "content": t}
                         for t in _DISTRACTOR_TURNS[bank_idx]],
        })
    return sessions


def _check_distractors(record_old: dict, record_new_value: str, predicate: str) -> None:
    import re
    gold_tokens = {str(record_old), str(record_new_value)}
    gold_tokens.update(_FORBIDDEN[predicate])
    for session in _DISTRACTOR_TURNS:
        for turn in session:
            for token in gold_tokens:
                if re.search(r"\b" + re.escape(token.lower()) + r"\b", turn.lower()):
                    raise ValueError(
                        f"distractor turn contains scenario token {token!r}: {turn!r}")


def main() -> None:
    v1_path = ROOT / "datasets" / "evolution_probe" / "probe.jsonl"
    rng = random.Random(20260325)
    out_records = []
    for line in v1_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        meta = rec.get("metadata") or {}
        predicate = str(meta.get("predicate") or "residence")
        _check_distractors(str(meta.get("old_value")), str(meta.get("new_value")),
                           predicate if predicate in _FORBIDDEN else "like")
        distractors = _distractor_sessions(rng)
        # Interleave: distractors carry dates across the whole window; the
        # final store keeps real sessions first then distractors, matching
        # the adapter's ingestion order (session order, not date order).
        rec["sessions"] = rec["sessions"] + distractors
        rec["metadata"] = dict(meta)
        rec["metadata"]["probe_version"] = 2
        rec["metadata"]["n_distractor_sessions"] = N_DISTRACTORS
        rec["metadata"]["normalization"] = "evolution_probe_v2"
        out_records.append(rec)
    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out_records),
        encoding="utf-8",
    )
    print(f"wrote {len(out_records)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
