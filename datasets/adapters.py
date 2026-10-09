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



def _answer_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        parts = [str(x).strip() for x in value if str(x).strip()]
        return " / ".join(parts) if parts else None
    if isinstance(value, dict):
        for key in ("answer", "text", "content", "value"):
            if value.get(key) is not None:
                return str(value[key])
    return str(value)


def _locomo_turns(conversation: Any) -> list[dict[str, Any]]:
    """Flatten LoCoMo sessions using the exact turn-indexing rule of MemoryEngine.

    MemoryEngine increments its per-session turn counter only after a non-empty
    message is ingested. The adapter must do the same; using the raw list index
    causes every subsequent provenance ID to drift after an empty message.
    """
    if not isinstance(conversation, dict):
        return []
    raw_sessions = conversation.get("conversation") or conversation.get("sessions") or []
    turns = []
    if isinstance(raw_sessions, dict):
        raw_sessions = [
            {"session_id": sid, "messages": messages}
            for sid, messages in raw_sessions.items()
        ]
    for session_idx, session in enumerate(raw_sessions if isinstance(raw_sessions, list) else []):
        if not isinstance(session, dict):
            continue
        source_id = str(
            session.get("session_id")
            or session.get("id")
            or f"session_{session_idx}"
        )
        messages = session.get("messages") or session.get("turns") or []
        if isinstance(messages, dict):
            messages = [messages]
        # Match MemoryEngine._add_claimed: turn_counter advances only for
        # messages that actually reach AddMessage (non-empty content).
        engine_turn_idx = 0
        for msg_idx, message in enumerate(messages if isinstance(messages, list) else []):
            text = _message_text(message).strip()
            if not text:
                continue
            if isinstance(message, dict):
                benchmark_turn_id = str(
                    message.get("turn_id")
                    or message.get("dia_id")
                    or message.get("message_id")
                    or message.get("id")
                    or f"turn_{msg_idx}"
                )
                role = str(message.get("role") or message.get("speaker") or "")
                timestamp = message.get("timestamp")
            else:
                benchmark_turn_id = f"turn_{msg_idx}"
                role = "user"
                timestamp = None
            turns.append({
                "turn_id": f"{source_id}:turn_{engine_turn_idx}",
                "source_id": source_id,
                "benchmark_turn_id": benchmark_turn_id,
                "text": text,
                "role": role,
                "timestamp": timestamp,
            })
            engine_turn_idx += 1
    return turns

def _locomo_evidence(raw_evidence: Any, *, example_id: str, conversation: Any) -> list[dict[str, Any]]:
    turns = _locomo_turns(conversation)
    by_turn = {t["turn_id"]: t for t in turns}
    by_benchmark_turn = {t["benchmark_turn_id"]: t for t in turns}
    by_text = {t["text"].strip(): t for t in turns}
    if raw_evidence is None:
        return []
    if isinstance(raw_evidence, (str, int, float)):
        raw_evidence = [raw_evidence]
    elif isinstance(raw_evidence, dict):
        raw_evidence = [raw_evidence]
    result = []
    for idx, item in enumerate(raw_evidence if isinstance(raw_evidence, list) else []):
        if isinstance(item, dict):
            evidence_id = _first(item, "evidence_id", "memory_id", default=f"{example_id}:e{idx}")
            turn_ref = _first(item, "turn_id", "turn", "dia_id", "dialogue_id", "source_turn_id", "message_id")
            source_ref = _first(item, "source_id", "session_id", "source", "doc_id")
            text = _first(item, "text", "content", "evidence", "memory", default="")
        else:
            evidence_id, turn_ref, source_ref, text = f"{example_id}:e{idx}", None, None, str(item)
        turn = by_turn.get(str(turn_ref)) if turn_ref is not None else None
        if turn is None and turn_ref is not None:
            turn = by_benchmark_turn.get(str(turn_ref))
        if turn is None and str(source_ref or "") in by_turn:
            turn = by_turn[str(source_ref)]
        if turn is None and str(text).strip() in by_text:
            turn = by_text[str(text).strip()]
        if turn is not None:
            result.append({
                "evidence_id": str(evidence_id),
                "source_id": turn["source_id"] or None,
                "turn_id": turn["turn_id"],
                "timestamp": turn.get("timestamp"),
                "text": turn["text"],
                "role": turn.get("role", ""),
                "granularity": "turn",
            })
        else:
            result.append({
                "evidence_id": str(evidence_id),
                "source_id": str(source_ref) if source_ref is not None else None,
                "turn_id": str(turn_ref) if turn_ref is not None else None,
                "timestamp": item.get("timestamp") if isinstance(item, dict) else None,
                "text": str(text or ""),
                "role": str(item.get("role") or item.get("speaker") or "") if isinstance(item, dict) else "",
                "granularity": "unresolved",
            })
    return result


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


def normalize_locomo_refined(raw: dict[str, Any], *, index: int, conversation: dict[str, Any] | None = None) -> dict[str, Any]:
    qid = str(_first(raw, "qa_id", "question_id", "id", default=index))
    sample_id = _first(raw, "sample_id", "conversation_id")
    conversation = conversation or {}
    answer = raw.get("answer")
    raw_evidence = _first(raw, "evidence", "gold_evidence", "supporting_evidence")
    evidence = _locomo_evidence(
        raw_evidence,
        example_id=f"locomo_refined_public:{qid}",
        conversation=conversation,
    )
    task = [str(raw.get("category"))] if raw.get("category") is not None else []
    return {
        "dataset": "locomo_refined_public",
        "family": "LoCoMo-Refined",
        "split": "public",
        "example_id": f"locomo_refined_public:{qid}",
        "conversation_id": str(sample_id) if sample_id is not None else None,
        "question_id": qid,
        "question": str(raw.get("question", "")),
        "answer": _answer_text(answer),
        "gold_evidence": evidence,
        "conversation": conversation,
        "task_type": task,
        "metadata": {
            "conversation_idx": raw.get("conversation_idx"),
            "qa_index": raw.get("qa_index"),
            "raw": raw,
            "normalization": "locomo_refined_v2_turn_provenance",
            "evidence_resolution": {
                "resolved_turns": sum(
                    1 for e in evidence if e.get("granularity") == "turn"
                ),
                "unresolved": sum(
                    1 for e in evidence if e.get("granularity") == "unresolved"
                ),
            },
        },
    }
