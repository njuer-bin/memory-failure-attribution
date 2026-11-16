"""Small controlled pilot for status drift under recursive conversational-memory compression.

Standard library only; calls a local Ollama-compatible /api/chat endpoint.
This is a synthetic pilot runner, not a benchmark or a source of confirmatory claims.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "status_drift_v2_pilot"
DEPTHS = (1, 2, 3, 5)
BUDGETS = {1: 220, 2: 180, 3: 140, 4: 120, 5: 100}
TOPICS = [
    "购买电脑", "去上海工作", "申请研究生", "参加数学建模比赛", "开始学习日语",
    "申请海外交换", "报名马拉松", "换一份工作", "开始健身", "开一家网店",
]


def build_dataset(limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dim in ("epistemic", "intentional", "conditional"):
        for i, action in enumerate(TOPICS):
            updated = (i % 2 == 1)
            if dim == "epistemic":
                initial = f"我可能会{action}，但现在还不能确定。"
                final = (f"我已经确认会{action}，这不是猜测了。" if updated
                         else f"目前仍然只是可能，我还没有确认会{action}。")
                gold, labels = ("CERTAIN" if updated else "POSSIBLE"), ("POSSIBLE", "CERTAIN")
            elif dim == "intentional":
                initial = f"我正在考虑{action}，还没有作出决定。"
                final = (f"我已经决定要{action}，会按这个计划推进。" if updated
                         else f"我仍然只是在考虑{action}，没有作出承诺。")
                gold, labels = ("COMMITTED" if updated else "CONSIDERING"), ("CONSIDERING", "COMMITTED")
            else:
                initial = f"如果拿到奖学金，我才考虑{action}。"
                final = (
                    f"我已经拿到奖学金了，所以这个条件已经满足；我现在开始考虑{action}。"
                    if updated else f"奖学金还没有结果，所以条件尚未满足；我暂时不考虑{action}。"
                )
                gold, labels = (
                    "CONDITION_SATISFIED" if updated else "CONDITION_ACTIVE",
                    ("CONDITION_ACTIVE", "CONDITION_SATISFIED"),
                )
            turns = [
                {"turn_id": 1, "text": initial},
                {"turn_id": 2, "text": "顺便说一下，最近天气变化很大，我还在整理日程。"},
                {"turn_id": 3, "text": final},
                {"turn_id": 4, "text": "今天还处理了课程作业和一些日常事务。"},
            ]
            rows.append({
                "sample_id": f"{dim}_{i:02d}", "dimension": dim, "proposition": action,
                "has_legitimate_update": updated, "gold_status": gold,
                "allowed_labels": list(labels), "evidence_turn_ids": [3] if updated else [1, 3],
                "turns": turns,
                "dialogue": "\n".join(f"[Turn {t['turn_id']}] {t['text']}" for t in turns),
            })
    if not 1 <= limit <= len(rows):
        raise ValueError(f"--limit must be between 1 and {len(rows)}")
    selected = []
    by_dim = {d: [r for r in rows if r["dimension"] == d]
              for d in ("epistemic", "intentional", "conditional")}
    while len(selected) < limit:
        for dim in by_dim:
            if by_dim[dim] and len(selected) < limit:
                selected.append(by_dim[dim].pop(0))
    return selected


def chat(base_url: str, model: str, messages: list[dict[str, str]],
         timeout: int, retries: int) -> str:
    url = base_url.rstrip("/") + "/api/chat"
    payload = {"model": model, "messages": messages, "stream": False,
               "options": {"temperature": 0, "num_predict": 220}}
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(
            url, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            content = data.get("message", {}).get("content", "")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("empty model response")
            return content.strip()
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Ollama request failed: {type(last_error).__name__}: {last_error}")


def parse_json(text: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            return value
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, flags=re.S)
    if match:
        try:
            value = json.loads(match.group(0))
            if isinstance(value, dict):
                return value
        except json.JSONDecodeError:
            pass
    return {"status": "PARSE_ERROR", "proposition_retained": None, "reason": text[:500]}


def writer_prompt(source: str, budget: int) -> list[dict[str, str]]:
    # Keep the system prompt identical across direct and recursive conditions.
    # Only the source supplied to the writer differs.
    system = (
        "你负责维护长期对话记忆。请把输入内容压缩成一条简洁记忆，忠实保留命题、"
        "确定性、用户意图强度和条件是否满足。不得把可能改成确定、考虑改成承诺，"
        "也不得删除仍然有效的条件。只有输入中明确出现的新证据才允许更新状态。"
        "不要补充推断，不要输出解释。"
    )
    user = f"请将以下内容压缩为不超过约 {budget} 个中文字符的一条记忆：\n\n{source}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def judge_prompt(sample: dict[str, Any], text: str) -> list[dict[str, str]]:
    labels = "、".join(sample["allowed_labels"])
    system = (
        "你是严格的对话状态标注员。只根据给定文本判断目标命题的最终状态。"
        "必须综合文本中的时间顺序和后续证据；如果后续明确更新，采用有证据支持的最终状态。"
        "如果命题未保留，proposition_retained=false。不要根据常识补充信息。"
        '只输出JSON：{"status":"标签","proposition_retained":true,"reason":"简短理由"}'
    )
    user = (f"研究维度：{sample['dimension']}\n目标命题：{sample['proposition']}\n"
            f"允许标签：{labels}\n待判断文本：\n{text}\n请给出最终状态标签。")
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def judge(sample: dict[str, Any], text: str, args: argparse.Namespace) -> dict[str, Any]:
    raw = chat(args.base_url, args.judge_model or args.writer_model,
               judge_prompt(sample, text), args.timeout, args.retries)
    parsed = parse_json(raw)
    status = str(parsed.get("status", "PARSE_ERROR")).strip().upper()
    if status not in sample["allowed_labels"]:
        status = "OMITTED" if status in ("OMITTED", "NOT_MENTIONED") else "INVALID_LABEL"
    retained = parsed.get("proposition_retained")
    if not isinstance(retained, bool):
        retained = None
    return {"status": status, "proposition_retained": retained,
            "reason": str(parsed.get("reason", "")), "raw_response": raw}


def compress(source: str, depth: int, args: argparse.Namespace) -> str:
    return chat(args.base_url, args.writer_model, writer_prompt(source, BUDGETS[depth]),
                args.timeout, args.retries)


def evaluate_condition(rows: list[dict[str, Any]], condition: str,
                       depth: int | None = None) -> dict[str, Any]:
    items = []
    for row in rows:
        if condition == "raw":
            prediction = row.get("raw_judgment")
        elif condition == "direct":
            prediction = row.get("direct_judgments", {}).get(str(depth))
        else:
            prediction = row.get("recursive_judgments", {}).get(str(depth))
        if prediction and prediction.get("status") not in ("INVALID_LABEL", "PARSE_ERROR"):
            items.append((row, prediction))
    n = len(items)
    correct = sum(pred["status"] == row["gold_status"] for row, pred in items)
    retained = [(row, pred) for row, pred in items if pred.get("proposition_retained") is True]
    distorted = sum(pred["status"] != row["gold_status"] for row, pred in retained)
    omitted = sum(pred.get("proposition_retained") is False or pred["status"] == "OMITTED"
                  for _, pred in items)
    updates = [(row, pred) for row, pred in items if row["has_legitimate_update"]]
    by_dimension = {}
    for dim in ("epistemic", "intentional", "conditional"):
        group = [(row, pred) for row, pred in items if row["dimension"] == dim]
        by_dimension[dim] = {
            "n": len(group),
            "accuracy": (sum(p["status"] == r["gold_status"] for r, p in group) / len(group)
                         if group else None),
        }
    return {
        "n_valid": n, "accuracy": correct / n if n else None, "correct": correct,
        "proposition_retained_n": len(retained),
        "cpsd": distorted / len(retained) if retained else None,
        "cpsd_numerator": distorted,
        "omission_rate": omitted / n if n else None, "omission_numerator": omitted,
        "legitimate_transition_accuracy": (
            sum(p["status"] == r["gold_status"] for r, p in updates) / len(updates)
            if updates else None
        ),
        "legitimate_transition_n": len(updates), "by_dimension": by_dimension,
    }


def summarize(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "protocol": "status_drift_recursive_pilot_v1",
        "writer_model": args.writer_model, "judge_model": args.judge_model or args.writer_model,
        "base_url": args.base_url, "requested_limit": args.limit,
        "completed_trajectories": len(rows),
        "conditions": {"raw": evaluate_condition(rows, "raw")},
        "warning": "Exploratory synthetic pilot only. Same-model writer/judge results are vulnerable "
                   "to correlated bias. Manually adjudicate outputs before making claims.",
    }
    for depth in DEPTHS:
        summary["conditions"][f"direct_d{depth}"] = evaluate_condition(rows, "direct", depth)
        summary["conditions"][f"recursive_d{depth}"] = evaluate_condition(rows, "recursive", depth)
    summary["recursive_minus_direct_error_rate"] = {}
    for depth in DEPTHS:
        direct = summary["conditions"][f"direct_d{depth}"]
        recursive = summary["conditions"][f"recursive_d{depth}"]
        summary["recursive_minus_direct_error_rate"][str(depth)] = (
            (1 - recursive["accuracy"]) - (1 - direct["accuracy"])
            if direct["accuracy"] is not None and recursive["accuracy"] is not None else None
        )
    return summary


def run(args: argparse.Namespace) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records_path = OUT / "records.jsonl"
    config_path = OUT / "run_config.json"
    summary_path = OUT / "summary.json"
    config = {
        "writer_model": args.writer_model, "judge_model": args.judge_model or args.writer_model,
        "base_url": args.base_url, "limit": args.limit, "depths": list(DEPTHS),
        "budgets_chars": BUDGETS, "temperature": 0,
    }
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    completed: dict[str, dict[str, Any]] = {}
    if args.resume and records_path.exists():
        for line in records_path.read_text(encoding="utf-8").splitlines():
            try:
                obj = json.loads(line)
                is_complete = (
                    obj.get("raw_judgment") is not None
                    and all(str(d) in obj.get("direct_judgments", {}) for d in DEPTHS)
                    and all(str(d) in obj.get("recursive_judgments", {}) for d in DEPTHS)
                    and not obj.get("errors")
                )
                if (is_complete and obj.get("writer_model") == args.writer_model
                        and obj.get("judge_model") == config["judge_model"]):
                    completed[obj["sample_id"]] = obj
            except (json.JSONDecodeError, KeyError):
                continue

    samples = build_dataset(args.limit)
    mode = "a" if args.resume and records_path.exists() else "w"
    with records_path.open(mode, encoding="utf-8") as out:
        for index, sample in enumerate(samples, 1):
            if sample["sample_id"] in completed:
                continue
            print(f"[{index}/{len(samples)}] {sample['sample_id']}", flush=True)
            row: dict[str, Any] = {
                **sample, "writer_model": args.writer_model, "judge_model": config["judge_model"],
                "raw_judgment": None, "direct_memories": {}, "direct_judgments": {},
                "recursive_memories": {}, "recursive_judgments": {}, "errors": [],
            }
            try:
                row["raw_judgment"] = judge(sample, sample["dialogue"], args)
                recursive_memory = sample["dialogue"]
                for depth in range(1, 6):
                    recursive_memory = compress(recursive_memory, depth, args)
                    row["recursive_memories"][str(depth)] = recursive_memory
                    if depth in DEPTHS:
                        row["recursive_judgments"][str(depth)] = judge(sample, recursive_memory, args)
                for depth in DEPTHS:
                    direct_memory = compress(sample["dialogue"], depth, args)
                    row["direct_memories"][str(depth)] = direct_memory
                    row["direct_judgments"][str(depth)] = judge(sample, direct_memory, args)
            except Exception as exc:
                row["errors"].append(f"{type(exc).__name__}: {exc}")
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            out.flush()
            completed[sample["sample_id"]] = row

    summary = summarize(list(completed.values()), args)
    summary["errors"] = [
        {"sample_id": row["sample_id"], "errors": row.get("errors", [])}
        for row in completed.values() if row.get("errors")
    ]
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--writer-model", default="qwen2.5:7b")
    parser.add_argument("--judge-model", default=None,
                        help="Use a separate judge model if available; defaults to writer model.")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--limit", type=int, default=6,
                        help="Number of trajectories (1-30); default 6 is a smoke test.")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.limit <= 30:
        parser.error("--limit must be between 1 and 30")
    run(args)


if __name__ == "__main__":
    main()
