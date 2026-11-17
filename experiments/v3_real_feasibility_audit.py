"""Stage 1 — real-dialogue feasibility audit for status fidelity.

Pre-screens LoCoMo-Refined and LongMemEval for propositions that carry an
epistemic, intentional, or conditional status, together with the original
evidence span. This is a *candidate generator*: automated matches over-generate,
and the human screening sheet measures their precision and labelability.

Outputs (under results/status_drift_v3_real_audit/):
  candidates.csv        all detected candidates
  screening_50.csv      balanced 50-item human audit sheet (rating columns blank)
  screening_A.csv       blank annotator A copy
  screening_B.csv       blank annotator B copy
  analysis/feasibility_summary.json

Usage:
  G:/aconda/python.exe -m experiments.v3_real_feasibility_audit
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

SEED_TARGET_PER_DATASET = 25
MAX_PER_SOURCE = 2

MARKERS = {
    "epistemic": [
        r"\bi think\b", r"\bi guess\b", r"\bmaybe\b", r"\bperhaps\b",
        r"\bprobably\b", r"\bpossibly\b", r"\bnot sure\b", r"\bi'm not sure\b",
        r"\bi believe\b", r"\bdefinitely\b", r"\bcertainly\b", r"\bfor sure\b",
        r"\blikely\b", r"\bunlikely\b", r"\bi wonder\b", r"\bi doubt\b",
        r"\bno idea\b", r"\bi don't know\b", r"\bseems like\b",
        r"\bapparently\b", r"\bsupposedly\b",
    ],
    "intentional": [
        r"\bi'm planning\b", r"\bi plan\b", r"\bi'm going to\b", r"\bi will\b",
        r"\bi'm thinking (of|about)\b", r"\bi'm considering\b",
        r"\bi want to\b", r"\bi'd like to\b", r"\bi intend\b",
        r"\bi decided\b", r"\bi've decided\b", r"\bi'm committed\b",
        r"\bi signed up\b", r"\bi registered\b", r"\bi booked\b",
        r"\bi'm scheduled\b", r"\bi hope to\b", r"\bi'm trying to\b",
        r"\bi might\b", r"\bi may\b", r"\bi'm supposed to\b",
        r"\bi have to\b", r"\bi need to\b", r"\bi'm about to\b",
        r"\bi'm leaning toward",
    ],
    "conditional": [
        r"\bif (i|we)\b", r"\bunless\b", r"\bas long as\b",
        r"\bdepending on\b", r"\bin case\b", r"\bonly if\b",
        r"\bonce (i|we)\b", r"\bconditional on\b", r"\bprovided that\b",
        r"\bcontingent on\b",
    ],
}

COMPILED = {
    dim: [re.compile(p) for p in patterns] for dim, patterns in MARKERS.items()
}

FIRST_PERSON = re.compile(r"\b(i|i'm|i've|i'd|i'll|my|me|we|we're|our)\b")
CHANGE = re.compile(
    r"\b(actually|changed|change of plans?|no longer|not anymore|instead|"
    r"cancel+ed|switch+ed|ended up|revised|update|but now|these days|"
    r"decided against|gave up)\b"
)
ACTION = re.compile(
    r"\b(apply|applied|applying|sign(ed)? up|signing up|register(ed|ing)?|"
    r"book(ed|ing)?|plan(s|ned|ning)?|start(ed|ing)?|begin|began|move|moving|"
    r"moved|buy|bought|buying|get|getting|adopt(ed|ing)?|host(ing|ed)?|"
    r"set up|open(ing|ed)?|launch(ed|ing)?|visit(ing|ed)?|attend(ing|ed)?|"
    r"join(ed|ing)?|learn(ing|ed)?|take|taking|took|go|going|went|"
    r"travel(ing|ed)?|work(ing|ed)?|stud(y|ying|ied)|cook(ing|ed)?|"
    r"bak(e|ing|ed)|paint(ing|ed)?|writ(e|ing)|wrote|publish(ing|ed)?|"
    r"sell(ing)?|sold|hire(d)?|rent(ing|ed)?|schedul(e|ed|ing)|"
    r"cancel(led|ed|ing)?|switch(ed|ing)?|try|trying|tried|find|finding|"
    r"consider(ing|ed)?|provide|providing|offer(ing|ed)?|help(ing|ed)?|"
    r"incorporate|use|using|link(ing|ed)?|pack(ing|ed)?|save|saving|"
    r"upgrade|focus|order(ing|ed)?|participat(e|ing|ed)?)\b"
)
TIME = re.compile(
    r"\b(today|tomorrow|tonight|next (week|month|year|weekend|few)|"
    r"this (week|month|year|weekend|summer)|in (a|one|two|three|\d+) "
    r"(day|week|month|year)s?|soon|later|eventually|in the future|"
    r"at the end of|on (monday|tuesday|wednesday|thursday|friday|saturday|"
    r"sunday)|january|february|march|april|may|june|july|august|september|"
    r"october|november|december)\b"
)
VAGUE = re.compile(
    r"\b(let you know|keep you posted|tell you|see how it goes|stay positive|"
    r"channel my grief|keep reaching|pass it on|make sure|keep track|"
    r"get back on track|get a better grip|be there for|support you|proud of|"
    r"happy for|good luck|sounds like|that's great|i hope you|make a change|"
    r"lift others up|keep using my voice|work together|join forces|"
    r"reach my dreams|achieve great things|make a difference|keep me going|"
    r"help people|take time to enjoy|do more ads|in the future|"
    r"what i deserve)\b"
)
PROCEDURAL = re.compile(
    r"\b(let you know|keep you posted|tell you|check out those|reach out|"
    r"take a look|hear from|see if)\b"
)
EPI_ADVICE = re.compile(
    r"\b(i think|i guess|i believe) (you|he|she|they|it|a |an |the |this |that )"
)
EPI_SELF = re.compile(
    r"\b(i think|i believe|i guess|i know|i doubt|i wonder|not sure|"
    r"i'm not sure|maybe|perhaps|probably|definitely|certainly|for sure|"
    r"there's a chance)\b.{0,20}\b(i|i'm|i've|i'd|i'll|my|we|we're|our)\b"
)
PAST_EVAL = re.compile(
    r"\b(definitely|certainly|for sure)\b.*\b(made|was|were|had|went|felt|"
    r"loved|enjoyed|appreciated)\b"
)
EXCLUDE = re.compile(
    r"(would .{0,60} if (i|we) could|could definitely|made sure|"
    r"trying to remember|\brealized\b|\bonce i (read|was|went|had|saw|met|tried)\b)"
)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
STOPWORDS = {
    "the", "and", "that", "this", "with", "have", "just", "like", "about",
    "really", "would", "could", "should", "there", "their", "them", "then",
    "than", "what", "when", "where", "which", "your", "you", "you're", "i'm",
    "i've", "it's", "don't", "didn't", "for", "been", "very", "much", "some",
    "also", "into", "over", "from", "will", "can't", "know", "think", "going",
    "want", "want", "get", "got", "make", "made", "one", "two", "now", "day",
    "time", "lot", "good", "great",
}


def content_words(text: str) -> set[str]:
    words = re.findall(r"[a-z']{4,}", text.lower())
    return {w for w in words if w not in STOPWORDS}


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENT_SPLIT.split(text) if s.strip()]


def detect(sentence: str) -> tuple[list[str], list[str], str | None]:
    lower = sentence.lower()
    dims, hits = [], []
    primary, primary_pos = None, None
    for dim, patterns in COMPILED.items():
        dim_hit = False
        for pattern in patterns:
            for match in pattern.finditer(lower):
                dims.append(dim)
                hits.append(match.group(0))
                dim_hit = True
                if primary_pos is None or match.start() < primary_pos:
                    primary, primary_pos = dim, match.start()
        if not dim_hit:
            continue
    return dims, hits, primary


def quality(sentence: str, dims: list[str], update: bool) -> int:
    lower = sentence.lower()
    score = len(set(dims))
    if len(dims) == 1:
        score += 1
    if ACTION.search(lower) and FIRST_PERSON.search(lower):
        score += 2
    if TIME.search(lower):
        score += 1
    if update:
        score += 2
    if VAGUE.search(lower):
        score -= 4
    if PROCEDURAL.search(lower):
        score -= 2
    if EPI_ADVICE.search(lower):
        score -= 2
    if PAST_EVAL.search(lower):
        score -= 2
    if "epistemic" in dims and not EPI_SELF.search(lower) \
            and not lower.lstrip().startswith(("i ", "i'", "we ", "we'")):
        score -= 2
    if EXCLUDE.search(lower):
        score -= 5
    if set(dims) == {"epistemic"} and not ACTION.search(lower):
        score -= 4
    if set(dims) == {"conditional"} and not ACTION.search(lower):
        score -= 5
    if 8 <= len(sentence.split()) <= 40:
        score += 1
    return score


def lme_date(text: str) -> datetime | None:
    m = re.match(r"(\d{4})/(\d{2})/(\d{2})", text.strip())
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def locomo_date(text: str) -> datetime | None:
    try:
        return datetime.strptime(text.strip(), "%I:%M %p on %d %B, %Y")
    except ValueError:
        return None


def make_candidate(dataset, source_id, session_index, date, speaker,
                   sentence, context, dims, hits, primary, update_text,
                   later_mention="", extra=None):
    return {
        "dataset": dataset,
        "source_id": source_id,
        "session_index": session_index,
        "date": date,
        "speaker": speaker,
        "target_sentence": sentence,
        "context": context,
        "dimensions": ",".join(sorted(set(dims))),
        "primary_dimension": primary,
        "matched_markers": ";".join(hits),
        "potential_update": "yes" if update_text else "no",
        "update_evidence": update_text or "",
        "later_mention": later_mention,
        "auto_score": quality(sentence, dims, bool(update_text)),
        "extra": extra or "",
    }


def find_update(candidates, messages, key_words, start_idx, time_key=None):
    """Return the first later message that re-mentions the topic with a change cue."""
    later = messages[start_idx + 1:]
    if time_key:
        later = [m for m in later if time_key(m) is not None]
    for message in later:
        if message.get("speaker") == "assistant":
            continue
        text = message["text"]
        overlap = content_words(text) & key_words
        if len(overlap) >= 2 and CHANGE.search(text.lower()):
            return text.strip()[:300]
    return None


def find_later_mention(messages, idx, key_words) -> str:
    """Return the first later *session* that re-mentions the topic, if any."""
    current = messages[idx].get("session_index")
    for message in messages[idx + 1:]:
        if message.get("speaker") == "assistant":
            continue
        if message.get("session_index") == current:
            continue
        if len(content_words(message["text"]) & key_words) >= 2:
            return str(message.get("session_index", ""))
    return ""


def scan_locomo(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            conv = json.loads(line)
            sample_id = conv["sample_id"]
            flat = []
            for session in conv["sessions"]:
                session_index = session["session_index"]
                date_text = session.get("date_time", "")
                date = locomo_date(date_text)
                for message in session["messages"]:
                    if not message.get("text"):
                        continue
                    flat.append({
                        "dia_id": message.get("dia_id", ""),
                        "speaker": message.get("speaker", ""),
                        "text": message["text"],
                        "date": date,
                        "session_index": session_index,
                        "date_text": date_text,
                    })
            for idx, message in enumerate(flat):
                for sentence in split_sentences(message["text"]):
                    if sentence.endswith("?"):
                        continue
                    dims, hits, primary = detect(sentence)
                    if not dims or not FIRST_PERSON.search(sentence.lower()):
                        continue
                    if len(sentence.split()) < 6:
                        continue
                    key_words = content_words(sentence)
                    update = find_update(rows, flat, key_words, idx)
                    if quality(sentence, dims, bool(update)) < 4:
                        continue
                    later = find_later_mention(flat, idx, key_words)
                    context = build_context(flat, idx)
                    rows.append(make_candidate(
                        "locomo", sample_id, message["session_index"],
                        message["date_text"], message["speaker"], sentence,
                        context, dims, hits, primary, update, later,
                        extra=f"dia_id={message['dia_id']}",
                    ))
    return rows


def build_context(messages, idx, before=1, after=1) -> str:
    lo = max(0, idx - before)
    hi = min(len(messages), idx + after + 1)
    parts = []
    for j in range(lo, hi):
        m = messages[j]
        prefix = ">> " if j == idx else ""
        text = m["text"] if j == idx else m["text"][:240]
        parts.append(f"{prefix}{m['speaker']}: {text[:700]}")
    return " | ".join(parts)


def scan_lme(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for instance in data:
        question_id = instance["question_id"]
        question_type = instance["question_type"]
        sessions = instance["haystack_sessions"]
        dates = instance.get("haystack_dates") or [""] * len(sessions)
        # chronological order, keep original index for context
        order = sorted(range(len(sessions)),
                       key=lambda i: lme_date(dates[i]) or datetime.min)
        flat = []
        for pos, i in enumerate(order):
            for message in sessions[i]:
                if not message.get("content"):
                    continue
                flat.append({
                    "speaker": message.get("role", ""),
                    "text": message["content"],
                    "date": lme_date(dates[i]),
                    "session_index": pos + 1,
                    "date_text": dates[i],
                })
        for idx, message in enumerate(flat):
            if message["speaker"] != "user":
                continue
            for sentence in split_sentences(message["text"]):
                if sentence.endswith("?"):
                    continue
                dims, hits, primary = detect(sentence)
                if not dims or not FIRST_PERSON.search(sentence.lower()):
                    continue
                if len(sentence.split()) < 6:
                    continue
                key_words = content_words(sentence)
                update = find_update(rows, flat, key_words, idx)
                if quality(sentence, dims, bool(update)) < 4:
                    continue
                later = find_later_mention(flat, idx, key_words)
                context = build_context(flat, idx)
                rows.append(make_candidate(
                    "longmemeval", question_id, message["session_index"],
                    message["date_text"], "user", sentence, context, dims,
                    hits, primary, update, later,
                    extra=f"question_type={question_type}",
                ))
    return rows


def dedupe(rows: list[dict]) -> list[dict]:
    seen, out = set(), []
    for row in rows:
        key = (row["dataset"], row["source_id"],
               re.sub(r"[^a-z0-9 ]", "", row["target_sentence"].lower()))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def select(rows: list[dict]) -> list[dict]:
    buckets = defaultdict(list)
    for row in rows:
        buckets[(row["dataset"], row["primary_dimension"])].append(row)
    for key in buckets:
        buckets[key].sort(key=lambda r: (-int(r["auto_score"]),
                                         r["source_id"], r["session_index"]))
    chosen, per_source, seen_text = [], Counter(), set()
    seen_words: list[set[str]] = []

    def text_key(row):
        return re.sub(r"[^a-z0-9 ]", "", row["target_sentence"].lower())

    def near_duplicate(row):
        words = content_words(row["target_sentence"])
        if not words:
            return False
        for other in seen_words:
            union = len(words | other)
            if union and len(words & other) / union >= 0.8:
                return True
        return False

    datasets = sorted({r["dataset"] for r in rows})
    dims = ["intentional", "epistemic", "conditional", None]
    progress = True
    while progress:
        progress = False
        for dataset in datasets:
            if sum(1 for r in chosen if r["dataset"] == dataset) >= \
                    SEED_TARGET_PER_DATASET:
                continue
            for dim in dims:
                bucket = buckets.get((dataset, dim))
                if not bucket:
                    continue
                while bucket:
                    row = bucket.pop(0)
                    key = text_key(row)
                    if per_source[row["source_id"]] >= MAX_PER_SOURCE \
                            or key in seen_text or near_duplicate(row):
                        continue
                    chosen.append(row)
                    per_source[row["source_id"]] += 1
                    seen_text.add(key)
                    seen_words.append(content_words(row["target_sentence"]))
                    progress = True
                    break
                if sum(1 for r in chosen if r["dataset"] == dataset) >= \
                        SEED_TARGET_PER_DATASET:
                    break
    target = SEED_TARGET_PER_DATASET * len(datasets)
    if len(chosen) < target:
        for row in sorted(rows, key=lambda r: -int(r["auto_score"])):
            if len(chosen) >= target:
                break
            key = text_key(row)
            if per_source[row["source_id"]] >= MAX_PER_SOURCE \
                    or key in seen_text or near_duplicate(row):
                continue
            chosen.append(row)
            per_source[row["source_id"]] += 1
            seen_text.add(key)
            seen_words.append(content_words(row["target_sentence"]))
    chosen.sort(key=lambda r: (r["dataset"], r["primary_dimension"] or "zz",
                               r["source_id"]))
    for i, row in enumerate(chosen, 1):
        row["candidate_id"] = f"RD-{i:03d}"
    return chosen


SCREEN_COLUMNS = [
    "status_bearing", "dimension", "proposition_clear",
    "evidence_sufficient", "lexical_cue_present", "lexical_labelable",
    "semantic_labelable", "update_present", "difficulty_1_3", "notes",
]


def write_sheet(path: Path, rows: list[dict]) -> None:
    base = ["candidate_id", "dataset", "source_id", "session_index", "date",
            "speaker", "target_sentence", "context", "dimensions",
            "primary_dimension", "matched_markers", "potential_update",
            "update_evidence", "later_mention", "auto_score", "extra"]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=base + SCREEN_COLUMNS,
                                extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            record = dict(row)
            for column in SCREEN_COLUMNS:
                record[column] = ""
            writer.writerow(record)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--locomo", default="locomo_refined_dataset/public/conversations.jsonl")
    parser.add_argument("--longmemeval", default="longmemeval_oracle.json")
    parser.add_argument("--out-dir", default="results/status_drift_v3_real_audit")
    args = parser.parse_args()

    rows = scan_locomo(Path(args.locomo)) + scan_lme(Path(args.longmemeval))
    rows = dedupe(rows)
    for i, row in enumerate(rows, 1):
        row["candidate_id"] = f"C{i:04d}"

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "analysis").mkdir(exist_ok=True)

    base = ["candidate_id", "dataset", "source_id", "session_index", "date",
            "speaker", "target_sentence", "context", "dimensions",
            "primary_dimension", "matched_markers", "potential_update",
            "update_evidence", "later_mention", "auto_score", "extra"]
    with (out / "candidates.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=base, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    chosen = select(rows)
    write_sheet(out / "screening_50.csv", chosen)
    write_sheet(out / "screening_A.csv", chosen)
    write_sheet(out / "screening_B.csv", chosen)

    by_dataset_dim = Counter((r["dataset"], r["primary_dimension"]) for r in rows)
    summary = {
        "all_candidates": len(rows),
        "by_dataset_dimension": {f"{d}/{dim}": n for (d, dim), n in
                                  sorted(by_dataset_dim.items(),
                                         key=lambda kv: str(kv[0]))},
        "potential_updates": sum(1 for r in rows if r["potential_update"] == "yes"),
        "later_mentions": sum(1 for r in rows if r["later_mention"]),
        "screening_later_mentions": sum(1 for r in chosen if r["later_mention"]),
        "screening_items": len(chosen),
        "screening_by_dataset": dict(Counter(r["dataset"] for r in chosen)),
        "screening_by_dimension": dict(Counter(r["primary_dimension"] for r in chosen)),
        "unique_sources": {
            "all": len({(r["dataset"], r["source_id"]) for r in rows}),
            "screening": len({(r["dataset"], r["source_id"]) for r in chosen}),
        },
        "note": "Automated candidate detection; over-generates. Human screening "
                "columns are blank and must be filled by two independent annotators.",
    }
    (out / "analysis" / "feasibility_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
