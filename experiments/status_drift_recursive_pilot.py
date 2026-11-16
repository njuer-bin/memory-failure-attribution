"""Controlled pilot for status drift under recursive conversational-memory compression.

Standard library only; calls a local Ollama-compatible /api/chat endpoint.
Synthetic pilot runner, not a benchmark or a source of confirmatory claims.

Design v2 (protocol v2.1) adds a crossed topic x update design, a neutral writer
control, deterministic proposition retention, and seed pinning. Design v1
behavior is preserved as the default for reproducibility of smoke_001.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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
TOPIC_KEYWORDS = {
    "购买电脑": ["购买电脑", "买电脑", "电脑"],
    "去上海工作": ["去上海", "上海工作", "上海"],
    "申请研究生": ["申请研究生", "研究生", "读研"],
    "参加数学建模比赛": ["数学建模", "建模比赛", "建模", "参赛"],
    "开始学习日语": ["学习日语", "日语"],
    "申请海外交换": ["海外交换", "交换"],
    "报名马拉松": ["马拉松"],
    "换一份工作": ["换一份工作", "换工作", "跳槽"],
    "开始健身": ["健身"],
    "开一家网店": ["开一家网店", "开网店", "网店"],
}
DIMENSIONS = ("epistemic", "intentional", "conditional")

# Deterministic condition-status markers for the conditional dimension. Checked
# before the satisfied markers so negations such as 未拿到奖学金 cannot match
# 拿到奖学金 as a substring.
CONDITION_NEGATIONS = [
    "未拿到奖学金", "没拿到奖学金", "没有拿到奖学金", "拿不到奖学金",
    "未拿奖学金", "未获奖学金", "没有获奖学金", "未获得奖学金",
    "无奖学金", "没有奖学金",
]
CONDITION_SATISFIED_MARKERS = [
    "条件已满足", "条件满足", "已满足条件", "已经满足",
    "拿到奖学金", "获得奖学金", "获奖学金",
    "已拿到奖学金", "已经拿到奖学金", "已获奖学金", "已经获得奖学金", "已获得奖学金",
]
CONDITION_ACTIVE_MARKERS = [
    "条件未满足", "条件不满足", "未满足", "尚未满足",
    "奖学金还没有结果", "奖学金未", "暂不考虑",
]


def det_condition_status(text: str) -> str:
    if any(marker in text for marker in CONDITION_NEGATIONS):
        return "ACTIVE"
    satisfied = any(marker in text for marker in CONDITION_SATISFIED_MARKERS)
    active = any(marker in text for marker in CONDITION_ACTIVE_MARKERS)
    if satisfied and active:
        return "AMBIGUOUS"
    if satisfied:
        return "SATISFIED"
    if active:
        return "ACTIVE"
    return "OMITTED"


def _make_row(dimension: str, action: str, updated: bool, sample_id: str,
              conditional_version: str = "v21") -> dict[str, Any]:
    if dimension == "epistemic":
        initial = f"我可能会{action}，但现在还不能确定。"
        final = (f"我已经确认会{action}，这不是猜测了。" if updated
                 else f"目前仍然只是可能，我还没有确认会{action}。")
        gold, labels = ("CERTAIN" if updated else "POSSIBLE"), ("POSSIBLE", "CERTAIN")
    elif dimension == "intentional":
        initial = f"我正在考虑{action}，还没有作出决定。"
        final = (f"我已经决定要{action}，会按这个计划推进。" if updated
                 else f"我仍然只是在考虑{action}，没有作出承诺。")
        gold, labels = ("COMMITTED" if updated else "CONSIDERING"), ("CONSIDERING", "COMMITTED")
    else:
        initial = f"如果拿到奖学金，我才考虑{action}。"
        if conditional_version == "v22":
            # State only the condition, never the action status; otherwise both
            # judges read the action clause and the label becomes ambiguous.
            final = ("我已经拿到奖学金了，条件已经满足。" if updated
                     else "奖学金还没有结果，条件尚未满足。")
        else:
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
    return {
        "sample_id": sample_id, "dimension": dimension, "proposition": action,
        "proposition_keywords": TOPIC_KEYWORDS[action],
        "has_legitimate_update": updated, "gold_status": gold,
        "allowed_labels": list(labels), "evidence_turn_ids": [3] if updated else [1, 3],
        "turns": turns,
        "dialogue": "\n".join(f"[Turn {t['turn_id']}] {t['text']}" for t in turns),
    }


def _build_dataset_v1(limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dim in DIMENSIONS:
        for i, action in enumerate(TOPICS):
            rows.append(_make_row(dim, action, i % 2 == 1, f"{dim}_{i:02d}"))
    if not 1 <= limit <= len(rows):
        raise ValueError(f"--limit must be between 1 and {len(rows)}")
    selected = []
    by_dim = {d: [r for r in rows if r["dimension"] == d] for d in DIMENSIONS}
    while len(selected) < limit:
        for dim in by_dim:
            if by_dim[dim] and len(selected) < limit:
                selected.append(by_dim[dim].pop(0))
    return selected


def _build_dataset_v2(limit: int, conditional_version: str = "v21",
                      topics_count: int = 5) -> list[dict[str, Any]]:
    """Crossed design: for each topic, both stable and updated variants."""
    rows: list[dict[str, Any]] = []
    for topic_idx, action in enumerate(TOPICS[:topics_count]):
        for updated in (False, True):
            for dim in DIMENSIONS:
                variant = "U" if updated else "S"
                rows.append(_make_row(dim, action, updated, f"{dim}_{topic_idx:02d}_{variant}",
                                      conditional_version))
    if not 1 <= limit <= len(rows):
        raise ValueError(f"--limit must be between 1 and {len(rows)}")
    return rows[:limit]


def build_dataset(limit: int, design: str = "v1", topics_count: int = 5) -> list[dict[str, Any]]:
    if design == "v3":
        return _build_dataset_v2(limit, "v22", topics_count)
    if design == "v2":
        return _build_dataset_v2(limit, "v21", topics_count)
    return _build_dataset_v1(limit)


def select_samples(limit: int, design: str, dimensions: str,
                   topics_count: int = 5) -> list[dict[str, Any]]:
    allowed = {d.strip() for d in dimensions.split(",") if d.strip()}
    if not allowed:
        raise ValueError("--dimensions must name at least one dimension")
    max_rows = 30 if design == "v1" else 6 * topics_count
    samples = build_dataset(max_rows, design, topics_count)
    samples = [s for s in samples if s["dimension"] in allowed]
    if not samples:
        raise ValueError(f"no samples for dimensions {sorted(allowed)}")
    if limit > len(samples):
        raise ValueError(f"--limit {limit} exceeds {len(samples)} available trajectories")
    return samples[:limit]


def chat(base_url: str, model: str, messages: list[dict[str, str]],
         timeout: int, retries: int, seed: int | None = None) -> str:
    url = base_url.rstrip("/") + "/api/chat"
    options: dict[str, Any] = {"temperature": 0, "num_predict": 220}
    if seed is not None:
        options["seed"] = seed
    payload = {"model": model, "messages": messages, "stream": False, "options": options}
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


def writer_prompt(source: str, budget: int, style: str = "status_aware") -> list[dict[str, str]]:
    if style == "neutral":
        system = ("你负责维护长期对话记忆。请把输入内容压缩成一条简洁记忆，"
                  "保留重要信息。不要输出解释。")
    elif style == "commitment_aware":
        system = (
            "你负责维护长期对话记忆。请把输入内容压缩成一条简洁记忆。"
            "如果用户对目标行动表达了明确决定或承诺，必须保留明确的承诺词"
            "（例如“已决定”“已承诺”“会按计划执行”），不得把它弱化为“推进计划”"
            "“计划中”“开始考虑”或只写行动本身。保留命题、确定性和条件是否满足。"
            "不要补充推断，不要输出解释。"
        )
    elif style == "sidecar":
        system = (
            "你负责维护长期对话记忆。请把输入内容压缩成一条简洁记忆，输出必须包含两行：\n"
            "第一行：压缩后的记忆正文，必须保留命题和重要信息。\n"
            "第二行：结构化状态，格式为\n"
            "[状态: 确定性=已确认|可能|不适用；意图=已决定|考虑中|不适用；"
            "条件=已满足|未满足|不适用]\n"
            "只填写输入中明确涉及的状态字段，其余写“不适用”。状态行不能替代正文。\n"
            "示例：\n"
            "用户可能购买电脑，近期天气变化大，正在整理日程。\n"
            "[状态: 确定性=可能；意图=不适用；条件=不适用]\n"
            "不要输出解释。"
        )
    else:
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
               judge_prompt(sample, text), args.timeout, args.retries, args.seed)
    parsed = parse_json(raw)
    status = str(parsed.get("status", "PARSE_ERROR")).strip().upper()
    if status not in sample["allowed_labels"]:
        status = "OMITTED" if status in ("OMITTED", "NOT_MENTIONED") else "INVALID_LABEL"
    retained = parsed.get("proposition_retained")
    if not isinstance(retained, bool):
        retained = None
    return {"status": status, "proposition_retained": retained,
            "reason": str(parsed.get("reason", "")), "raw_response": raw}


def compress_budget(source: str, budget: int, args: argparse.Namespace) -> str:
    return chat(args.base_url, args.writer_model,
                writer_prompt(source, budget, args.writer_style),
                args.timeout, args.retries, args.seed)


def compress(source: str, depth: int, args: argparse.Namespace) -> str:
    return compress_budget(source, BUDGETS[depth], args)


def rewrite_matched_budget_schedule(depth: int) -> list[int]:
    """d chained calls whose intermediate budgets stay at BUDGETS[1]."""
    return [BUDGETS[1]] * (depth - 1) + [BUDGETS[depth]]


def compress_rewrite_matched(sample: dict[str, Any], args: argparse.Namespace) -> dict[str, str]:
    memories: dict[str, str] = {}
    base = compress(sample["dialogue"], 1, args)
    for depth in (2, 3, 5):
        memory = base
        for budget in rewrite_matched_budget_schedule(depth)[1:]:
            memory = compress_budget(memory, budget, args)
        memories[str(depth)] = memory
    return memories


def topic_mentioned(text: str, sample: dict[str, Any]) -> bool:
    """Weak lexical diagnostic only; it is NOT proposition-retention evidence."""
    keywords = sample.get("proposition_keywords") or [sample["proposition"]]
    return any(keyword in text for keyword in keywords)


def text_size(text: str) -> dict[str, int]:
    """Length diagnostics; Unicode characters/UTF-8 bytes are not token counts."""
    return {"characters": len(text), "utf8_bytes": len(text.encode("utf-8"))}


def _prediction(row: dict[str, Any], condition: str, depth: int | None) -> dict | None:
    if condition == "raw":
        return row.get("raw_judgment")
    key = {
        "direct": "direct_judgments",
        "recursive": "recursive_judgments",
        "rewrite_matched": "rewrite_matched_judgments",
    }[condition]
    return (row.get(key) or {}).get(str(depth))


def _memory(row: dict[str, Any], condition: str, depth: int | None) -> str:
    if condition == "raw":
        return row.get("dialogue", "")
    key = {
        "direct": "direct_memories",
        "recursive": "recursive_memories",
        "rewrite_matched": "rewrite_matched_memories",
    }[condition]
    return (row.get(key) or {}).get(str(depth), "")


def _topic_mention_check(row: dict[str, Any], condition: str, depth: int | None) -> bool:
    if condition != "raw":
        key = {
            "direct": "direct_topic_mention",
            "recursive": "recursive_topic_mention",
            "rewrite_matched": "rewrite_matched_topic_mention",
        }[condition]
        value = (row.get(key) or {}).get(str(depth))
        if value is not None:
            return bool(value)
    return topic_mentioned(_memory(row, condition, depth), row)


def evaluate_condition(rows: list[dict[str, Any]], condition: str,
                       depth: int | None = None) -> dict[str, Any]:
    items = []
    for row in rows:
        prediction = _prediction(row, condition, depth)
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
    for dim in DIMENSIONS:
        group = [(row, pred) for row, pred in items if row["dimension"] == dim]
        by_dimension[dim] = {
            "n": len(group),
            "accuracy": (sum(p["status"] == r["gold_status"] for r, p in group) / len(group)
                         if group else None),
        }

    det_pairs = [(row, pred) for row in rows
                 for pred in [_prediction(row, condition, depth)]
                 if pred and pred.get("status") not in ("INVALID_LABEL", "PARSE_ERROR")
                 and _topic_mention_check(row, condition, depth)]
    det_distorted = sum(pred["status"] != row["gold_status"] for row, pred in det_pairs)
    det_omitted = sum(not _topic_mention_check(row, condition, depth) for row in rows)

    cond_rows = [row for row in rows if row["dimension"] == "conditional"]

    def _cond_of(row: dict[str, Any]) -> str:
        if condition == "raw":
            return det_condition_status(row.get("dialogue", ""))
        key = {
            "direct": "direct_condition",
            "recursive": "recursive_condition",
            "rewrite_matched": "rewrite_matched_condition",
        }[condition]
        stored = (row.get(key) or {}).get(str(depth))
        return stored or det_condition_status(_memory(row, condition, depth))

    cond_actual = [_cond_of(row) for row in cond_rows]
    cond_expected = ["SATISFIED" if row["gold_status"] == "CONDITION_SATISFIED" else "ACTIVE"
                     for row in cond_rows]
    cond_correct = sum(a == e for a, e in zip(cond_actual, cond_expected))
    cond_omitted = sum(a == "OMITTED" for a in cond_actual)
    cond_ambiguous = sum(a == "AMBIGUOUS" for a in cond_actual)

    return {
        "n_valid": n, "accuracy": correct / n if n else None, "correct": correct,
        "proposition_retained_n": len(retained),
        "cpsd_judge_provisional": distorted / len(retained) if retained else None,
        "cpsd_judge_provisional_numerator": distorted,
        "judge_claimed_proposition_retained_n": len(retained),
        "metric_warning": "Judge-claimed proposition retention is not human-adjudicated; this conditional error rate is provisional, not confirmatory CPSD.",
        "omission_rate": omitted / n if n else None, "omission_numerator": omitted,
        "legitimate_transition_accuracy": (
            sum(p["status"] == r["gold_status"] for r, p in updates) / len(updates)
            if updates else None
        ),
        "legitimate_transition_n": len(updates), "by_dimension": by_dimension,
        "topic_mention_check_n": len(rows),
        "topic_mentioned_n": len(rows) - det_omitted,
        "topic_not_mentioned_rate": det_omitted / len(rows) if rows else None,
        "status_error_given_topic_mention": det_distorted / len(det_pairs) if det_pairs else None,
        "topic_mention_warning": "Lexical topic mention does not establish proposition identity, polarity, relation, or semantic retention.",
        "condition_marker_heuristic_warning": "Rule-based Chinese marker matching is a diagnostic sanity check, not a semantic gold label.",
        "condition_marker_heuristic_n": len(cond_rows),
        "condition_marker_heuristic_correct": cond_correct,
        "condition_marker_heuristic_accuracy": cond_correct / len(cond_rows) if cond_rows else None,
        "condition_marker_heuristic_omitted_n": cond_omitted,
        "condition_marker_heuristic_ambiguous_n": cond_ambiguous,
        "condition_marker_heuristic_omission_rate": cond_omitted / len(cond_rows) if cond_rows else None,
    }


def summarize(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    protocol_by_design = {
        "v1": "status_drift_recursive_pilot_v1",
        "v2": "status_drift_recursive_pilot_v2.1",
        "v3": "status_drift_recursive_pilot_v2.2",
    }
    summary: dict[str, Any] = {
        "protocol": "status_drift_recursive_pilot_v2.4",
        "protocol_parent_design": protocol_by_design[args.design],
        "design": args.design, "writer_style": args.writer_style, "seed": args.seed,
        "writer_model": args.writer_model, "judge_model": args.judge_model or args.writer_model,
        "base_url": args.base_url, "requested_limit": args.limit,
        "dimensions": args.dimensions,
        "completed_trajectories": len(rows),
        "conditions": {"raw": evaluate_condition(rows, "raw")},
        "warning": "Exploratory synthetic pilot only. Same-model writer/judge results are vulnerable "
                   "to correlated bias. Manually adjudicate outputs before making claims.",
    }
    for depth in DEPTHS:
        summary["conditions"][f"direct_d{depth}"] = evaluate_condition(rows, "direct", depth)
        summary["conditions"][f"recursive_d{depth}"] = evaluate_condition(rows, "recursive", depth)
    if args.rewrite_matched:
        for depth in DEPTHS:
            summary["conditions"][f"rewrite_matched_d{depth}"] = evaluate_condition(
                rows, "rewrite_matched", depth)
    summary["recursive_minus_direct_error_rate"] = {}
    for depth in DEPTHS:
        direct = summary["conditions"][f"direct_d{depth}"]
        recursive = summary["conditions"][f"recursive_d{depth}"]
        summary["recursive_minus_direct_error_rate"][str(depth)] = (
            (1 - recursive["accuracy"]) - (1 - direct["accuracy"])
            if direct["accuracy"] is not None and recursive["accuracy"] is not None else None
        )
    summary["recursive_minus_direct_provisional_status_error_given_topic_mention_delta"] = {}
    for depth in DEPTHS:
        direct = summary["conditions"][f"direct_d{depth}"]
        recursive = summary["conditions"][f"recursive_d{depth}"]
        summary["recursive_minus_direct_provisional_status_error_given_topic_mention_delta"][str(depth)] = (
            recursive["status_error_given_topic_mention"] - direct["status_error_given_topic_mention"]
            if direct["status_error_given_topic_mention"] is not None
            and recursive["status_error_given_topic_mention"] is not None else None
        )
    if args.rewrite_matched:
        summary["recursive_minus_rewrite_matched_error_rate"] = {}
        summary["rewrite_matched_minus_direct_error_rate"] = {}
        for depth in DEPTHS:
            recursive = summary["conditions"][f"recursive_d{depth}"]
            matched = summary["conditions"][f"rewrite_matched_d{depth}"]
            direct = summary["conditions"][f"direct_d{depth}"]
            summary["recursive_minus_rewrite_matched_error_rate"][str(depth)] = (
                (1 - recursive["accuracy"]) - (1 - matched["accuracy"])
                if recursive["accuracy"] is not None and matched["accuracy"] is not None else None
            )
            summary["rewrite_matched_minus_direct_error_rate"][str(depth)] = (
                (1 - matched["accuracy"]) - (1 - direct["accuracy"])
                if matched["accuracy"] is not None and direct["accuracy"] is not None else None
            )
    return summary


def run(args: argparse.Namespace) -> None:
    out_dir = Path(args.out_dir) if args.out_dir else (
        OUT if args.design == "v1" else OUT / ("v22" if args.design == "v3" else "v21")
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    records_path = out_dir / "records.jsonl"
    config_path = out_dir / "run_config.json"
    summary_path = out_dir / "summary.json"
    config = {
        "writer_model": args.writer_model, "judge_model": args.judge_model or args.writer_model,
        "base_url": args.base_url, "limit": args.limit, "depths": list(DEPTHS),
        "budgets_chars": BUDGETS, "temperature": 0, "design": args.design,
        "writer_style": args.writer_style, "seed": args.seed, "skip_judge": args.skip_judge,
        "dimensions": args.dimensions, "rewrite_matched": args.rewrite_matched,
        "topics": args.topics, "timeout": args.timeout, "retries": args.retries,
    }
    canonical_config = json.dumps(config, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    config_fingerprint = hashlib.sha256(canonical_config.encode("utf-8")).hexdigest()
    config["config_fingerprint"] = config_fingerprint

    if args.resume and records_path.exists():
        if not config_path.exists():
            raise RuntimeError("--resume refused: existing records have no run_config.json; use a new --out-dir.")
        previous_config = json.loads(config_path.read_text(encoding="utf-8"))
        if previous_config.get("config_fingerprint") != config_fingerprint:
            raise RuntimeError(
                "--resume refused: run configuration differs from existing output. "
                "Use the original configuration or a new --out-dir."
            )
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    completed: dict[str, dict[str, Any]] = {}
    if args.resume and records_path.exists():
        for line in records_path.read_text(encoding="utf-8").splitlines():
            try:
                obj = json.loads(line)
                is_complete = (
                    not obj.get("errors")
                    and (
                        (args.skip_judge
                         and all(str(d) in obj.get("direct_memories", {}) for d in DEPTHS)
                         and all(str(d) in obj.get("recursive_memories", {}) for d in DEPTHS))
                        or
                        (not args.skip_judge
                         and obj.get("raw_judgment") is not None
                         and all(str(d) in obj.get("direct_judgments", {}) for d in DEPTHS)
                         and all(str(d) in obj.get("recursive_judgments", {}) for d in DEPTHS))
                    )
                )
                if (is_complete and obj.get("config_fingerprint") == config_fingerprint):
                    completed[obj["sample_id"]] = obj
            except (json.JSONDecodeError, KeyError):
                continue

    samples = select_samples(args.limit, args.design, args.dimensions, args.topics)
    mode = "a" if args.resume and records_path.exists() else "w"
    with records_path.open(mode, encoding="utf-8") as out:
        for index, sample in enumerate(samples, 1):
            if sample["sample_id"] in completed:
                continue
            print(f"[{index}/{len(samples)}] {sample['sample_id']}", flush=True)
            row: dict[str, Any] = {
                **sample, "writer_model": args.writer_model, "judge_model": config["judge_model"],
                "design": args.design, "writer_style": args.writer_style, "seed": args.seed,
                "config_fingerprint": config_fingerprint,
                "raw_judgment": None, "direct_memories": {}, "direct_judgments": {},
                "direct_topic_mention": {}, "direct_condition": {}, "direct_memory_sizes": {},
                "recursive_memories": {}, "recursive_judgments": {},
                "recursive_topic_mention": {}, "recursive_condition": {}, "recursive_memory_sizes": {},
                "rewrite_matched_memories": {}, "rewrite_matched_judgments": {},
                "rewrite_matched_topic_mention": {}, "rewrite_matched_condition": {}, "rewrite_matched_memory_sizes": {},
                "errors": [],
            }
            try:
                if not args.skip_judge:
                    row["raw_judgment"] = judge(sample, sample["dialogue"], args)
                recursive_memory = sample["dialogue"]
                for depth in range(1, 6):
                    recursive_memory = compress(recursive_memory, depth, args)
                    row["recursive_memories"][str(depth)] = recursive_memory
                    row["recursive_topic_mention"][str(depth)] = topic_mentioned(recursive_memory, sample)
                    row["recursive_memory_sizes"][str(depth)] = text_size(recursive_memory)
                    row["recursive_condition"][str(depth)] = det_condition_status(recursive_memory)
                    if depth in DEPTHS and not args.skip_judge:
                        row["recursive_judgments"][str(depth)] = judge(sample, recursive_memory, args)
                for depth in DEPTHS:
                    direct_memory = compress(sample["dialogue"], depth, args)
                    row["direct_memories"][str(depth)] = direct_memory
                    row["direct_topic_mention"][str(depth)] = topic_mentioned(direct_memory, sample)
                    row["direct_memory_sizes"][str(depth)] = text_size(direct_memory)
                    row["direct_condition"][str(depth)] = det_condition_status(direct_memory)
                    if not args.skip_judge:
                        row["direct_judgments"][str(depth)] = judge(sample, direct_memory, args)
                if args.rewrite_matched:
                    row["rewrite_matched_memories"]["1"] = row["direct_memories"]["1"]
                    row["rewrite_matched_topic_mention"]["1"] = row["direct_topic_mention"]["1"]
                    row["rewrite_matched_memory_sizes"]["1"] = row["direct_memory_sizes"]["1"]
                    row["rewrite_matched_condition"]["1"] = row["direct_condition"]["1"]
                    if not args.skip_judge:
                        row["rewrite_matched_judgments"]["1"] = row["direct_judgments"]["1"]
                    matched = compress_rewrite_matched(sample, args)
                    for depth in (2, 3, 5):
                        memory = matched[str(depth)]
                        row["rewrite_matched_memories"][str(depth)] = memory
                        row["rewrite_matched_topic_mention"][str(depth)] = topic_mentioned(memory, sample)
                        row["rewrite_matched_memory_sizes"][str(depth)] = text_size(memory)
                        row["rewrite_matched_condition"][str(depth)] = det_condition_status(memory)
                        if not args.skip_judge:
                            row["rewrite_matched_judgments"][str(depth)] = judge(sample, memory, args)
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
                        help="Number of trajectories; v1 supports 1-30, v2 supports 1-30.")
    parser.add_argument("--design", choices=("v1", "v2", "v3"), default="v1",
                        help="v2 = crossed topic x update; v3 = v2 with fixed conditional turns.")
    parser.add_argument("--dimensions", default="epistemic,intentional,conditional",
                        help="Comma-separated dimensions to run.")
    parser.add_argument("--topics", type=int, choices=tuple(range(1, 11)), default=5,
                        help="Number of topics for design v2/v3 (max 10).")
    parser.add_argument("--writer-style",
                        choices=("status_aware", "neutral", "commitment_aware", "sidecar"),
                        default="status_aware")
    parser.add_argument("--skip-judge", action="store_true",
                        help="Only produce memories; judge later with the calibration runner.")
    parser.add_argument("--rewrite-matched", action="store_true",
                        help="Also run the chained constant-budget control (protocol v2.3).")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be at least 1")
    run(args)


if __name__ == "__main__":
    main()
