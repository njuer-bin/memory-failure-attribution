"""Judge v1.1 calibration for the status drift pilot.

Re-scores existing memories from records.jsonl without re-running the writer.
The v1.0 judge conflated condition-not-satisfied with proposition omission and
inverted CONDITION_ACTIVE / CONDITION_SATISFIED; this prompt separates the two
and defines every label explicitly.

Usage:
    python -I -m experiments.status_drift_judge_calibration --judge-model qwen2.5:7b
    python -I -m experiments.status_drift_judge_calibration --judge-model gemma3:12b
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.status_drift_recursive_pilot import DEPTHS, chat, parse_json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "status_drift_v2_pilot"

LABEL_DEFS = {
    "epistemic": (
        "- POSSIBLE: 说话人尚未确认目标命题，只是可能或不确定。\n"
        "- CERTAIN: 说话人明确确认目标命题（例如“已确认”“确定了”）。"
    ),
    "intentional": (
        "- CONSIDERING: 说话人在考虑目标行动，但还没有作出决定。\n"
        "- COMMITTED: 说话人明确决定或承诺执行目标行动。"
    ),
    "conditional": (
        "- CONDITION_ACTIVE: 目标行动所依赖的条件尚未满足、结果未知，或明确未达成。\n"
        "- CONDITION_SATISFIED: 对话明确说明该条件已经满足。"
    ),
}


def calibration_prompt(sample: dict, text: str) -> list[dict[str, str]]:
    labels = "、".join(sample["allowed_labels"])
    system = (
        "你是严格的对话状态标注员。只根据给定文本判断目标命题的最终状态。\n"
        "标签定义（必须严格按定义选择）：\n"
        f"{LABEL_DEFS[sample['dimension']]}\n"
        "规则：\n"
        "1. 按时间顺序综合全文；后续明确证据覆盖先前状态。\n"
        "2. 若后文明确确认，不要因为前文曾表示不确定而将状态降级。\n"
        "3. 不要把“条件未满足”理解为命题未保留；状态与命题保留是两个独立问题。\n"
        "4. proposition_retained 只问目标命题在文本中是否仍可识别，与它的状态无关。\n"
        "5. 只依据文本，不补充常识。\n"
        '只输出JSON：{"status":"标签","proposition_retained":true,'
        '"evidence":"支持该状态的原文片段","confidence":"high|medium|low"}'
    )
    user = (
        f"研究维度：{sample['dimension']}\n目标命题：{sample['proposition']}\n"
        f"允许标签：{labels}\n待判断文本：\n{text}\n请给出最终状态标签。"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def judge_v11(sample: dict, text: str, args) -> dict:
    raw = chat(args.base_url, args.judge_model, calibration_prompt(sample, text),
               args.timeout, args.retries)
    parsed = parse_json(raw)
    status = str(parsed.get("status", "PARSE_ERROR")).strip().upper()
    if status not in sample["allowed_labels"]:
        status = "INVALID_LABEL"
    retained = parsed.get("proposition_retained")
    if not isinstance(retained, bool):
        retained = None
    confidence = str(parsed.get("confidence", "")).strip().lower()
    return {
        "status": status,
        "proposition_retained": retained,
        "evidence": str(parsed.get("evidence", "")),
        "confidence": confidence if confidence in ("high", "medium", "low") else None,
        "raw_response": raw,
    }


def old_judgment(row: dict, condition: str) -> dict | None:
    if condition == "raw":
        return row.get("raw_judgment")
    kind, depth = condition.split("_d")
    key = "direct_judgments" if kind == "direct" else "recursive_judgments"
    return (row.get(key) or {}).get(depth)


def conditions_for(row: dict):
    yield "raw", row["dialogue"]
    for depth in DEPTHS:
        yield f"direct_d{depth}", row.get("direct_memories", {}).get(str(depth), "")
    for depth in DEPTHS:
        yield f"recursive_d{depth}", row.get("recursive_memories", {}).get(str(depth), "")


def aggregate(items: list[dict]) -> dict:
    valid = [x for x in items if x["new_status"] not in ("INVALID_LABEL", "PARSE_ERROR", "EMPTY_TEXT")]
    n = len(valid)
    correct = sum(x["new_status"] == x["gold_status"] for x in valid)
    retained = [x for x in valid if x["proposition_retained"] is True]
    distorted = sum(x["new_status"] != x["gold_status"] for x in retained)
    omitted = sum(x["proposition_retained"] is False for x in valid)
    updates = [x for x in valid if x["has_legitimate_update"]]
    old_valid = [x for x in items if x["old_status"] in ("POSSIBLE", "CERTAIN", "CONSIDERING",
                                                         "COMMITTED", "CONDITION_ACTIVE",
                                                         "CONDITION_SATISFIED")]
    agree = sum(x["new_status"] == x["old_status"] for x in valid
                if x["old_status"] is not None)
    return {
        "n_items": len(items),
        "n_valid": n,
        "accuracy": correct / n if n else None,
        "correct": correct,
        "proposition_retained_n": len(retained),
        "cpsd": distorted / len(retained) if retained else None,
        "cpsd_numerator": distorted,
        "omission_rate": omitted / n if n else None,
        "omission_numerator": omitted,
        "legitimate_transition_accuracy": (
            sum(x["new_status"] == x["gold_status"] for x in updates) / len(updates)
            if updates else None
        ),
        "legitimate_transition_n": len(updates),
        "old_accuracy_on_same_items": (
            sum(x["old_status"] == x["gold_status"] for x in old_valid) / len(old_valid)
            if old_valid else None
        ),
        "old_valid_n": len(old_valid),
        "new_vs_old_agreement": agree / n if n else None,
    }


def run(args) -> None:
    records_path = OUT / "records.jsonl"
    rows = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    slug = args.judge_model.replace(":", "_").replace("/", "_")
    out_path = OUT / f"judge_calibration_{slug}.jsonl"
    summary_path = OUT / f"judge_calibration_{slug}_summary.json"
    items: list[dict] = []
    with out_path.open("w", encoding="utf-8") as out:
        for row in rows:
            sample = {
                "dimension": row["dimension"],
                "proposition": row["proposition"],
                "allowed_labels": row["allowed_labels"],
            }
            for condition, text in conditions_for(row):
                old = old_judgment(row, condition) or {}
                item = {
                    "sample_id": row["sample_id"],
                    "dimension": row["dimension"],
                    "condition": condition,
                    "gold_status": row["gold_status"],
                    "has_legitimate_update": row["has_legitimate_update"],
                    "old_status": old.get("status"),
                    "text": text,
                }
                if not text.strip():
                    # Never let an indexing bug silently judge empty text; the
                    # model would default to an arbitrary label.
                    item.update({
                        "new_status": "EMPTY_TEXT",
                        "proposition_retained": None,
                        "evidence": "",
                        "confidence": None,
                        "raw_response": "",
                        "error": "EMPTY_TEXT: memory missing for this condition",
                    })
                    items.append(item)
                    out.write(json.dumps(item, ensure_ascii=False) + "\n")
                    out.flush()
                    continue
                try:
                    verdict = judge_v11(sample, text, args)
                    item.update({
                        "new_status": verdict["status"],
                        "proposition_retained": verdict["proposition_retained"],
                        "evidence": verdict["evidence"],
                        "confidence": verdict["confidence"],
                        "raw_response": verdict["raw_response"],
                        "error": None,
                    })
                except Exception as exc:  # keep failures visible, never coerce
                    item.update({
                        "new_status": "PARSE_ERROR",
                        "proposition_retained": None,
                        "evidence": "",
                        "confidence": None,
                        "raw_response": "",
                        "error": f"{type(exc).__name__}: {exc}",
                    })
                items.append(item)
                out.write(json.dumps(item, ensure_ascii=False) + "\n")
                out.flush()
                print(f"{item['sample_id']:<18} {condition:<14} gold={item['gold_status']:<18} "
                      f"old={item['old_status']:<18} new={item['new_status']:<18} "
                      f"retained={item['proposition_retained']}", flush=True)

    summary = {
        "protocol": "status_drift_judge_v1.1_calibration",
        "judge_model": args.judge_model,
        "source_records": str(records_path),
        "conditions": {
            cond: aggregate([x for x in items if x["condition"] == cond])
            for cond in ["raw"] + [f"direct_d{d}" for d in DEPTHS]
            + [f"recursive_d{d}" for d in DEPTHS]
        },
        "by_dimension": {
            dim: aggregate([x for x in items if x["dimension"] == dim])
            for dim in ("epistemic", "intentional", "conditional")
        },
        "warnings": [
            "Re-judging existing v1.0 memories; no writer re-run.",
            "Synthetic pilot, n=6; assistant adjudication is not human ground truth.",
        ],
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--judge-model", default="qwen2.5:7b")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
