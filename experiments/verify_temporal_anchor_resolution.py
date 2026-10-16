"""Verify whether relative-time predictions resolve to the reference answer
when anchored on the BENCHMARK evidence timestamp (LoCoMo session/message time,
not the engine ingestion timestamp).

For each audited case (wrong answer + full gold evidence in final context):
    1. parse the gold evidence timestamp string (e.g. "1:56 pm on 8 May, 2023")
    2. resolve the model's relative expression (yesterday / next month / this week ...)
    3. compare the resolved absolute date range with the reference answer

Output: per-case verdict + aggregate count of resolvable vs unresolvable.
"""
import json
import re
from datetime import datetime, timedelta

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}

RELATIVE_PATTERNS = [
    (r"\byesterday\b", "yesterday"),
    (r"\btoday\b", "today"),
    (r"\btomorrow\b", "tomorrow"),
    (r"\bnext month\b", "next_month"),
    (r"\blast month\b", "last_month"),
    (r"\bthis month\b", "this_month"),
    (r"\bnext week\b", "next_week"),
    (r"\blast week\b", "last_week"),
    (r"\bthis week\b", "this_week"),
    (r"\bnext year\b", "next_year"),
    (r"\blast year\b", "last_year"),
    (r"\bthis year\b", "this_year"),
]


def parse_benchmark_timestamp(text):
    """Parse LoCoMo-style timestamps: '1:56 pm on 8 May, 2023' / '3:19 pm on 15 August, 2023'."""
    if not text:
        return None
    m = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)\s+on\s+(\d{1,2})\s+([A-Za-z]+),?\s+(\d{4})", text)
    if not m:
        return None
    hh, mm, ap, day, mon, year = m.groups()
    mon_num = MONTHS.get(mon.lower())
    if not mon_num:
        return None
    hh = int(hh) % 12 + (12 if ap.lower() == "pm" else 0)
    try:
        return datetime(int(year), mon_num, int(day), hh, int(mm))
    except ValueError:
        return None


def parse_reference_dates(ref):
    """Extract all explicit dates from a reference answer."""
    dates = []
    for m in re.finditer(r"(\d{1,2})\s+([A-Za-z]+),?\s+(\d{4})", ref or ""):
        mon = MONTHS.get(m.group(2).lower())
        if mon:
            dates.append((int(m.group(3)), mon, int(m.group(1))))
    for m in re.finditer(r"([A-Za-z]+)\s+(\d{4})", ref or ""):
        mon = MONTHS.get(m.group(1).lower())
        if mon:
            dates.append((int(m.group(2)), mon, None))  # month granularity
    return dates


def resolve_relative(expr, anchor):
    """Resolve a relative expression against an anchor datetime -> (start, end, granularity)."""
    if expr == "yesterday":
        d = anchor.date() - timedelta(days=1)
        return (d, d, "day")
    if expr == "today":
        d = anchor.date()
        return (d, d, "day")
    if expr == "tomorrow":
        d = anchor.date() + timedelta(days=1)
        return (d, d, "day")
    if expr == "this_month":
        return (anchor.date().replace(day=1),
                (anchor.date().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1),
                "month")
    if expr == "next_month":
        first = (anchor.date().replace(day=28) + timedelta(days=4)).replace(day=1)
        last = (first.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return (first, last, "month")
    if expr == "last_month":
        first = anchor.date().replace(day=1) - timedelta(days=1)
        first = first.replace(day=1)
        return (first, anchor.date().replace(day=1) - timedelta(days=1), "month")
    if expr == "this_week":
        monday = anchor.date() - timedelta(days=anchor.weekday())
        return (monday, monday + timedelta(days=6), "week")
    if expr == "next_week":
        monday = anchor.date() - timedelta(days=anchor.weekday()) + timedelta(days=7)
        return (monday, monday + timedelta(days=6), "week")
    if expr == "last_week":
        monday = anchor.date() - timedelta(days=anchor.weekday()) - timedelta(days=7)
        return (monday, monday + timedelta(days=6), "week")
    if expr == "this_year":
        return (anchor.date().replace(month=1, day=1), anchor.date().replace(month=12, day=31), "year")
    if expr == "next_year":
        return (anchor.date().replace(year=anchor.year + 1, month=1, day=1),
                anchor.date().replace(year=anchor.year + 1, month=12, day=31), "year")
    if expr == "last_year":
        return (anchor.date().replace(year=anchor.year - 1, month=1, day=1),
                anchor.date().replace(year=anchor.year - 1, month=12, day=31), "year")
    return None


def date_in_range(d, rng):
    return rng[0] <= d <= rng[1]


def main():
    path = "results/oracle_experiments/comparison.jsonl"
    recs = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]

    targets = []
    for r in recs:
        real = r.get("modes", {}).get("real_memory", {})
        ans = real.get("answer") or {}
        if ans.get("correct"):
            continue
        ctx = real.get("context") or {}
        gold_count = r.get("gold_evidence_count") or 0
        if len(ctx.get("found") or []) < gold_count or gold_count == 0:
            continue
        if (real.get("answer_failure_type") or "").startswith("E0"):
            continue
        targets.append(r)

    print(f"Audited targets (wrong answer + full gold evidence in context): {len(targets)}\n")
    resolvable = 0
    for r in targets:
        qid = r["question_id"]
        pred = (r["modes"]["real_memory"]["answer"] or {}).get("answer", "")
        ref = r.get("gold_answer", "")
        evidence = r.get("gold_evidence") or []
        ts_texts = [ge.get("timestamp") for ge in evidence if ge.get("timestamp")]
        anchors = [t for t in (parse_benchmark_timestamp(x) for x in ts_texts) if t]

        expr = None
        for pat, name in RELATIVE_PATTERNS:
            if re.search(pat, (pred or "").lower()):
                expr = name
                break

        verdict = "UNRESOLVABLE"
        detail = ""
        if anchors and expr:
            rng = resolve_relative(expr, anchors[0])
            if rng:
                ref_dates = parse_reference_dates(ref)
                for (y, m, d) in ref_dates:
                    if d is None:  # month granularity reference
                        if rng[0].year == y and rng[0].month == m:
                            verdict = "RESOLVES_TO_REFERENCE"
                            detail = f"{expr} @ {anchors[0].date()} -> {rng[0]}..{rng[1]} ~ {ref}"
                            break
                    else:
                        from datetime import date
                        if date_in_range(date(y, m, d), rng):
                            verdict = "RESOLVES_TO_REFERENCE"
                            detail = f"{expr} @ {anchors[0].date()} -> {rng[0]}..{rng[1]} ~ {ref}"
                            break
                if verdict == "UNRESOLVABLE":
                    detail = f"{expr} @ {anchors[0].date()} -> {rng[0]}..{rng[1]} vs ref={ref} (dates={ref_dates})"
        elif not expr:
            detail = f"no relative expression in prediction: {pred!r}"
        else:
            detail = "no benchmark timestamp in gold evidence"

        if verdict == "RESOLVES_TO_REFERENCE":
            resolvable += 1
        print(f"[{qid}] {verdict}")
        print(f"   Q: {r['question'][:80]}")
        print(f"   pred: {pred[:60]!r}  ref: {ref[:60]!r}")
        print(f"   {detail}\n")

    print(f"{'='*70}")
    print(f"resolvable_to_reference: {resolvable}/{len(targets)}")


if __name__ == "__main__":
    main()
