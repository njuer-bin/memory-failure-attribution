"""Benchmark-aware adapters for datasets with known schemas."""
from __future__ import annotations
from typing import Any
from .normalize import _first, _evidence_items


def _message_text(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("content") or message.get("text") or message.get("message") or "")
    return str(message or "")


def _message_has_answer(message: Any) -> bool:
    return isinstance(message, dict) and bool(message.get("has_answer"))


def normalize_longmemeval(raw: dict[str, Any], *, dataset: str, index: int) -> dict[str, Any]:
    qid = str(raw.get("question_id", index))
    session_ids = raw.get("haystack_session_ids", []) or []
    dates = raw.get("haystack_dates", []) or []
    sessions = raw.get("haystack_sessions", []) or []
    answer_ids = {str(x) for x in (raw.get("answer_session_ids", []) or [])}

    conversation = []
    evidence = []
    for i, session in enumerate(sessions):
        sid = str(session_ids[i]) if i < len(session_ids) else f"session_{i}"
        date = dates[i] if i < len(dates) else None
        messages = list(session or []) if isinstance(session, list) else [session]
        item = {"session_id": sid, "date": date, "messages": messages}
        conversation.append(item)

        # LongMemEval annotates answer-bearing turns with has_answer. Prefer
        # turn-level evidence because session-level evidence overstates the
        # amount of information that must survive the memory lifecycle.
        answer_turns = [
            (j, m) for j, m in enumerate(messages) if _message_has_answer(m)
        ]
        if sid in answer_ids:
            if answer_turns:
                for j, message in answer_turns:
                    text = _message_text(message)
                    if text:
                        evidence.append({
                            "evidence_id": f"{qid}:{sid}:turn_{j}",
                            "source_id": sid,
                            "turn_id": f"{sid}:turn_{j}",
                            "timestamp": date,
                            "text": text,
                            "role": str(message.get("role") or message.get("speaker") or "") if isinstance(message, dict) else "",
                            "granularity": "turn",
                        })
            else:
                # Backward-compatible fallback for files without has_answer.
                evidence.append({
                    "evidence_id": f"{qid}:{sid}",
                    "source_id": sid,
                    "timestamp": date,
                    "text": "\n".join(_message_text(m) for m in messages if _message_text(m)),
                    "role": "",
                    "granularity": "session",
                })

    qtype = raw.get("question_type", "unknown")
    if str(qid).endswith("_abs"):
        qtype = f"{qtype},abstention"

    return {
        "dataset": dataset, "family": "LongMemEval", "split": None,
        "example_id": f"{dataset}:{qid}", "conversation_id": qid,
        "question_id": qid, "question": str(raw.get("question", "")),
        "answer": raw.get("answer"), "gold_evidence": evidence,
        "conversation": conversation, "task_type": [qtype],
        "metadata": {
            "question_date": raw.get("question_date"),
            "answer_session_ids": list(answer_ids),
            "gold_evidence_granularity": (
                "turn" if any(e.get("granularity") == "turn" for e in evidence)
                else "session"
            ),
            "raw": raw,
            "normalization": "longmemeval_v2_turn_level",
        },
    }


def normalize_locomo_refined(raw: dict[str, Any], *, index: int) -> dict[str, Any]:
    qid = str(_first(raw, "qa_id", "question_id", "id", default=index))
    sample_id = _first(raw, "sample_id", "conversation_id")
    answer = raw.get("answer")
    evidence = _evidence_items(
        _first(raw, "evidence", "gold_evidence", "supporting_evidence"),
        f"locomo_refined_public:{qid}",
    )
    task = [str(raw.get("category"))] if raw.get("category") is not None else []
    return {
        "dataset": "locomo_refined_public", "family": "LoCoMo-Refined",
        "split": "public", "example_id": f"locomo_refined_public:{qid}",
        "conversation_id": str(sample_id) if sample_id is not None else None,
        "question_id": qid, "question": str(raw.get("question", "")),
        "answer": answer, "gold_evidence": evidence, "conversation": [],
        "task_type": task,
        "metadata": {
            "conversation_idx": raw.get("conversation_idx"),
            "qa_index": raw.get("qa_index"), "raw": raw,
            "normalization": "locomo_refined_v1",
        },
    }
