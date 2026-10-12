"""Run the oracle experiment for one or more exact question IDs.

This is a thin targeted wrapper around ``run_oracle_experiments.run_record``.
It avoids rerunning the full benchmark when validating a provenance-sensitive
case after an evaluator change.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "oracle_experiments"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="locomo_refined_public")
    parser.add_argument(
        "--question-id",
        action="append",
        required=True,
        help="Exact normalized question ID. Repeat the option for multiple questions.",
    )
    args = parser.parse_args()

    # Keep CLI help usable in a lightweight CI environment. These imports pull
    # in the full experiment stack and are only needed after argument parsing.
    from datasets.loader import iter_normalized
    from experiments.run_oracle_experiments import run_record

    wanted = set(args.question_id)
    records = []
    for record in iter_normalized(args.dataset):
        if str(record.get("question_id")) in wanted:
            records.append(record)
            if len(records) == len(wanted):
                break

    found = {str(record.get("question_id")) for record in records}
    missing = sorted(wanted - found)
    if missing:
        raise SystemExit(
            "Question ID(s) not found in normalized dataset: " + ", ".join(missing)
        )

    OUT.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    results = []

    print("=" * 72, flush=True)
    print(
        f"Targeted oracle attribution: dataset={args.dataset}, "
        f"questions={len(records)}",
        flush=True,
    )
    print("=" * 72, flush=True)

    for idx, record in enumerate(records):
        question_id = str(record.get("question_id"))
        print(f"\n[{idx + 1}/{len(records)}] START question_id={question_id}", flush=True)
        t0 = time.perf_counter()
        row = run_record(record, idx)
        failure = row["modes"]["real_memory"].get("answer_failure_type")
        results.append(row)
        print(
            f"[{idx + 1}/{len(records)}] DONE {time.perf_counter() - t0:.2f}s "
            f"failure={failure}",
            flush=True,
        )

    output = {
        "dataset": args.dataset,
        "question_ids": [str(r.get("question_id")) for r in records],
        "records": len(results),
        "elapsed_seconds": time.perf_counter() - started,
        "results": results,
    }
    path = OUT / "targeted_attribution.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + json.dumps(output, ensure_ascii=False, indent=2), flush=True)
    print(f"\nSaved: {path}", flush=True)


if __name__ == "__main__":
    main()
