"""Controlled pilot for epistemic-status distortion during conversational memory compression.

Uses only the Python standard library and a local Ollama-compatible /api/chat endpoint.
No model training or external API is involved.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "epistemic_status_pilot"
STATUSES = ("FACT", "UNCERTAIN", "HYPOTHETICAL", "INTENTION", "NEGATED_INTENTION", "UNDECIDED")
TOPICS = [
    "换工作", "搬去上海", "买一辆电动车", "开始学日语", "报名考研",
    "养一只猫", "换一台电脑", "申请海外交换", "参加马拉松", "开始健身",
    "学钢琴", "买房", "读博士", "辞职", "转专业",
    "自己创业", "考驾照", "学做饭", "开始记账", "养一只狗",
    "去欧洲旅行", "换一套房子", "结婚", "要孩子", "投资基金",
    "开一家网店", "学习编程", "换手机", "做自由职业", "申请实习",
    "参加数学建模比赛", "准备英语考试", "搬到南京", "买一辆汽车",
    "开始跑步", "学习机器学习", "申请研究生", "去国外读书",
    "开源一个项目", "参加学术会议",
]


def build_dataset(limit_base: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for topic_idx, proposition in enumerate(TOPICS[:limit_base]):
        frames = {
            "FACT": f"我已经{proposition}了。",
            "UNCERTAIN": f"我可能会{proposition}，但目前还不能确定。",
            "HYPOTHETICAL": f"如果将来{proposition}，我会再考虑下一步；这只是设想。",
            "INTENTION": f"我打算{proposition}。",
            "NEGATED_INTENTION": f"我不打算{proposition}。",
            "UNDECIDED": f"我还没决定是否{proposition}。",
        }
        for status in STATUSES:
            utterance = frames[status]
            rows.append({
                "sample_id": f"topic{topic_idx:03d}_{status.lower()}",
                "topic_id": f"topic{topic_idx:03d}",
                "proposition": proposition,
                "gold_status": status,
                "utterance": utterance,
            })
    return rows


WRITER_SYSTEM = (
    "你是一个长期对话助手的记忆整理模块。请把用户刚刚说的内容整理成一条简洁、"
    "适合未来对话使用的记忆。只保留原话明确支持的信息，不要推断，不要补充。"
    "用自然中文写一条记忆，不要输出解释、标签或JSON。"
)
JUDGE_SYSTEM = """你是严格的语义标注员。判断给定文本对目标命题表达了什么状态。
必须区分已经成立的事实、可能性、假设、明确意图、明确不打算、尚未决定。
如果文本没有保留目标命题，status 输出 OMITTED。
只输出一个JSON对象，不要输出Markdown或额外文字：
{"status":"FACT|UNCERTAIN|HYPOTHETICAL|INTENTION|NEGATED_INTENTION|UNDECIDED|OMITTED","proposition_retained":true,"reason":"简短理由"}
不要把“可能”“如果”“打算”“不打算”“还没决定”互相等同。
"""

def ollama_chat(base_url: str, model: str, messages: list[dict[str, str]],
                timeout: int, max_retries: int) -> str:
    url = base_url.rstrip("/") + "/api/chat"
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 180},
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(
                url, data=body,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
            return str(data.get("message", {}).get("content", "")).strip()
        except Exception as exc:  # keep the pilot resumable and auditable
            last_error = exc
            if attempt < max_retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Ollama request failed: {type(last_error).__name__}: {last_error}")


def parse_json_object(text: str) -> dict[str, Any]:
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
    return {"status": "JUDGE_PARSE_ERROR", "proposition_retained": None, "reason": text[:500]}


def classify(text: str, proposition: str, base_url: str, model: str,
             timeout: int, max_retries: int) -> dict[str, Any]:
    user = (
        f"目标命题：用户{proposition}。\n"
        f"待判断文本：\n{text}\n\n"
        "请判断待判断文本是否保留目标命题，以及它对该命题表达的状态。"
    )
    raw = ollama_chat(base_url, model, [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": user},
    ], timeout, max_retries)
    result = parse_json_object(raw)
    status = str(result.get("status", "JUDGE_PARSE_ERROR")).upper()
    if status not in (*STATUSES, "OMITTED", "JUDGE_PARSE_ERROR"):
        status = "JUDGE_PARSE_ERROR"
    result["status"] = status
    result["raw_response"] = raw
    return result


def compress(utterance: str, base_url: str, model: str,
             timeout: int, max_retries: int) -> str:
    return ollama_chat(base_url, model, [
        {"role": "system", "content": WRITER_SYSTEM},
        {"role": "user", "content": utterance},
    ], timeout, max_retries)


def run(args: argparse.Namespace) -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    output_path = OUT / "pilot.jsonl"
    summary_path = OUT / "summary.json"
    rows = build_dataset(args.limit_base)
    completed: dict[str, dict[str, Any]] = {}
    if args.resume and output_path.exists():
        for line in output_path.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
                completed[item["sample_id"]] = item
            except (json.JSONDecodeError, KeyError):
                continue
    mode = "a" if args.resume and output_path.exists() else "w"
    errors = 0
    with output_path.open(mode, encoding="utf-8") as out:
        for idx, sample in enumerate(rows, 1):
            if sample["sample_id"] in completed:
                continue
            print(f"[{idx}/{len(rows)}] {sample['sample_id']}", flush=True)
            result: dict[str, Any] = {**sample, "model": args.model}
            try:
                raw_judgment = classify(
                    sample["utterance"], sample["proposition"], args.base_url,
                    args.model, args.timeout, args.max_retries,
                )
                memory = compress(
                    sample["utterance"], args.base_url, args.model,
                    args.timeout, args.max_retries,
                )
                compressed_judgment = classify(
                    memory, sample["proposition"], args.base_url,
                    args.model, args.timeout, args.max_retries,
                )
                result.update({
                    "raw_judgment": raw_judgment,
                    "compressed_memory": memory,
                    "compressed_judgment": compressed_judgment,
                    "error": None,
                })
            except Exception as exc:
                errors += 1
                result.update({
                    "raw_judgment": result.get("raw_judgment"),
                    "compressed_memory": result.get("compressed_memory"),
                    "compressed_judgment": None,
                    "error": f"{type(exc).__name__}: {exc}",
                })
            out.write(json.dumps(result, ensure_ascii=False) + "\n")
            out.flush()
    all_rows = list(completed.values())
    for line in output_path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            if item["sample_id"] not in {x["sample_id"] for x in all_rows}:
                all_rows.append(item)
        except (json.JSONDecodeError, KeyError):
            continue
    summary = summarize(all_rows, args)
    summary["run_errors_this_invocation"] = errors
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


def summarize(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    valid = [r for r in rows if r.get("raw_judgment") and r.get("compressed_judgment")]
    n = len(valid)
    raw_correct = sum(r["raw_judgment"]["status"] == r["gold_status"] for r in valid)
    comp_correct = sum(r["compressed_judgment"]["status"] == r["gold_status"] for r in valid)
    retained = [r for r in valid if r["compressed_judgment"].get("proposition_retained") is True
                and r["compressed_judgment"]["status"] != "OMITTED"]
    nonfact = [r for r in valid if r["gold_status"] != "FACT"]
    nonfact_valid = [r for r in nonfact if r["compressed_judgment"]["status"] != "OMITTED"]
    inflation = sum(r["compressed_judgment"]["status"] == "FACT" for r in nonfact_valid)
    negated = [r for r in valid if r["gold_status"] == "NEGATED_INTENTION"]
    negation_flip = sum(r["compressed_judgment"]["status"] in ("INTENTION", "FACT") for r in negated)
    status_error_raw = sum(r["raw_judgment"]["status"] != r["gold_status"] for r in valid)
    status_error_comp = sum(r["compressed_judgment"]["status"] != r["gold_status"] for r in valid)
    per_status: dict[str, Any] = {}
    for status in STATUSES:
        group = [r for r in valid if r["gold_status"] == status]
        per_status[status] = {
            "n": len(group),
            "raw_accuracy": sum(x["raw_judgment"]["status"] == status for x in group) / len(group) if group else None,
            "compressed_accuracy": sum(x["compressed_judgment"]["status"] == status for x in group) / len(group) if group else None,
            "compressed_predicted_statuses": dict(Counter(x["compressed_judgment"]["status"] for x in group)),
        }
    return {
        "protocol": "epistemic_status_compression_pilot_v1",
        "model": args.model,
        "base_url": args.base_url,
        "limit_base": args.limit_base,
        "total_inputs": len(rows),
        "valid_pairs": n,
        "failed_or_incomplete": len(rows) - n,
        "raw_status_accuracy": raw_correct / n if n else None,
        "compressed_status_accuracy": comp_correct / n if n else None,
        "raw_status_error_rate": status_error_raw / n if n else None,
        "compressed_status_error_rate": status_error_comp / n if n else None,
        "net_compression_error_delta": (status_error_comp - status_error_raw) / n if n else None,
        "status_preservation_given_proposition_retained": (
            sum(r["compressed_judgment"]["status"] == r["gold_status"] for r in retained) / len(retained)
            if retained else None
        ),
        "proposition_retained_count": len(retained),
        "proposition_omission_rate": (
            sum(r["compressed_judgment"]["status"] == "OMITTED" or
                r["compressed_judgment"].get("proposition_retained") is False for r in valid) / n
            if n else None
        ),
        "assertion_inflation_rate_among_nonfacts_not_omitted": inflation / len(nonfact_valid) if nonfact_valid else None,
        "assertion_inflation_numerator": inflation,
        "assertion_inflation_denominator": len(nonfact_valid),
        "negation_flip_rate": negation_flip / len(negated) if negated else None,
        "negation_flip_numerator": negation_flip,
        "negation_flip_denominator": len(negated),
        "per_status": per_status,
        "interpretation_warning": (
            "Pilot diagnostic only. Writer and judge are the same model in this initial implementation; "
            "manual adjudication and a second independent judge/model are required before scientific claims."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="qwen2.5:7b")
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--limit-base", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.limit_base < 1 or args.limit_base > len(TOPICS):
        parser.error(f"--limit-base must be between 1 and {len(TOPICS)}")
    run(args)


if __name__ == "__main__":
    main()
