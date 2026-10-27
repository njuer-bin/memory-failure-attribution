"""Build the controlled F3 Evolution probe (40 scenarios).

Each scenario is a tiny dated conversation whose ground-truth evidence path is
known exactly, so the lifecycle tracer can distinguish "the fact was never
formed" (F1) from "it was formed but the active state is wrong" (F3).

Families:

- update    same-predicate update, e.g. residence/workplace/like;
- stale     inverse-predicate state change ("like blue" -> "don't like blue");
- history   question asks for the superseded value, so evolution succeeds only
            if history is preserved.

Usage:
    python -m experiments.build_evolution_probe
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datasets" / "evolution_probe" / "probe.jsonl"

CITIES = [
    ("Beijing", "Shanghai"), ("Paris", "Lyon"), ("Berlin", "Munich"),
    ("Tokyo", "Osaka"), ("Toronto", "Vancouver"), ("Sydney", "Melbourne"),
    ("Madrid", "Barcelona"), ("Rome", "Milan"), ("Seoul", "Busan"),
    ("Lisbon", "Porto"),
]
COMPANIES = [
    ("Google", "Microsoft"), ("Amazon", "Meta"), ("IBM", "Oracle"),
    ("Intel", "Nvidia"), ("Siemens", "Bosch"), ("Sony", "Panasonic"),
    ("Adobe", "Figma"), ("Spotify", "Netflix"),
]
LIKES = [
    ("blue", "green"), ("coffee", "tea"), ("jazz", "classical music"),
    ("hiking", "cycling"), ("pasta", "sushi"), ("winter", "summer"),
    ("comedy", "documentaries"), ("painting", "photography"),
]
STALE = ["blue", "coffee", "jazz", "hiking", "pasta", "winter"]

DATES = ("2025-01-15", "2025-06-20", "2025-09-10")


def _session(sid: str, date: str, *contents: str) -> dict[str, Any]:
    return {
        "session_id": sid,
        "date": date,
        "messages": [{"role": "user", "content": text} for text in contents],
    }


def _record(
    qid: str,
    family: str,
    question: str,
    answer: str,
    sessions: list[dict[str, Any]],
    gold: list[tuple[str, int]],
    *,
    requires_history: bool = False,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "question_id": qid,
        "question": question,
        "answer": answer,
        "sessions": sessions,
        "gold_turns": [{"session_id": sid, "turn_index": idx} for sid, idx in gold],
        "requires_history": requires_history,
        "task_type": [family] + ([extra.pop("task_type")] if extra and "task_type" in extra else []),
        "metadata": {"evolution_family": family, **(extra or {})},
    }


def build() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    n = 0

    for old, new in CITIES:
        n += 1
        records.append(_record(
            f"evo_update_residence_{n:03d}", "update",
            "Where does the user currently live?", new,
            [_session("s1", DATES[0], f"I currently live in {old}."),
             _session("s2", DATES[1], "I work as a data analyst.",
                      f"I currently live in {new}.")],
            [("s2", 1)],
            extra={"old_value": old, "new_value": new, "predicate": "residence"},
        ))

    for old, new in COMPANIES:
        n += 1
        records.append(_record(
            f"evo_update_workplace_{n:03d}", "update",
            "Where does the user currently work?", new,
            [_session("s1", DATES[0], f"I currently work at {old}."),
             _session("s2", DATES[1], f"I currently work at {new}.")],
            [("s2", 0)],
            extra={"old_value": old, "new_value": new, "predicate": "workplace"},
        ))

    for old, new in LIKES:
        n += 1
        records.append(_record(
            f"evo_update_like_{n:03d}", "update",
            "What does the user currently like?", new,
            [_session("s1", DATES[0], f"I really like {old}."),
             _session("s2", DATES[1], f"I really like {new}.")],
            [("s2", 0)],
            extra={"old_value": old, "new_value": new, "predicate": "like"},
        ))

    for item in STALE:
        n += 1
        records.append(_record(
            f"evo_stale_{n:03d}", "stale",
            f"Does the user still like {item}?", "No",
            [_session("s1", DATES[0], f"I really like {item}."),
             _session("s2", DATES[1], f"I don't like {item} anymore.")],
            [("s2", 0)],
            extra={"old_value": item, "new_value": f"not {item}", "predicate": "like/dislike"},
        ))

    for old, new in CITIES[:8]:
        n += 1
        records.append(_record(
            f"evo_history_{n:03d}", "history",
            f"Where did the user live before moving to {new}?", old,
            [_session("s1", DATES[0], f"I currently live in {old}."),
             _session("s2", DATES[1], f"I currently live in {new}.")],
            [("s1", 0)],
            requires_history=True,
            extra={"old_value": old, "new_value": new, "predicate": "residence"},
        ))

    return records


def main() -> None:
    records = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )
    print(f"wrote {len(records)} scenarios to {OUT}")


if __name__ == "__main__":
    main()
