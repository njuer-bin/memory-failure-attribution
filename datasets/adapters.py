"""Benchmark-aware adapters for datasets with known schemas."""
from __future__ import annotations
from typing import Any
from .normalize import _first, _evidence_items

def normalize_longmemeval(raw: dict[str, Any], *, dataset: str, index: int) -> dict[str, Any]:
    qid=str(raw.get("question_id", index))
    session_ids=raw.get("haystack_session_ids", [])
    dates=raw.get("haystack_dates", [])
    sessions=raw.get("haystack_sessions", [])
    answer_ids=set(raw.get("answer_session_ids", []))
    conversation=[]
    evidence=[]
    for i,session in enumerate(sessions):
        sid=str(session_ids[i]) if i < len(session_ids) else f"session_{i}"
        date=dates[i] if i < len(dates) else None
        item={"session_id":sid,"date":date,"messages":session}
        conversation.append(item)
        if sid in answer_ids:
            evidence.append({"evidence_id":f"{qid}:{sid}","source_id":sid,"timestamp":date,"text":str(session)})
    qtype=raw.get("question_type","unknown")
    if str(qid).endswith("_abs"):
        qtype=f"{qtype},abstention"
    return {
        "dataset":dataset,"family":"LongMemEval","split":None,"example_id":f"{dataset}:{qid}",
        "conversation_id":qid,"question_id":qid,"question":str(raw.get("question","")),
        "answer":raw.get("answer"),"gold_evidence":evidence,"conversation":conversation,
        "task_type":[qtype],"metadata":{"question_date":raw.get("question_date"),"answer_session_ids":list(answer_ids),"raw":raw,"normalization":"longmemeval_v1"}
    }

def normalize_locomo_refined(raw: dict[str, Any], *, index: int) -> dict[str, Any]:
    qid=str(_first(raw,"qa_id","question_id","id",default=index))
    sample_id=_first(raw,"sample_id","conversation_id")
    answer=raw.get("answer")
    if isinstance(answer,list):
        answer_value=answer
    else:
        answer_value=answer
    evidence=_evidence_items(_first(raw,"evidence","gold_evidence","supporting_evidence"),f"locomo_refined_public:{qid}")
    task=[str(raw.get("category"))] if raw.get("category") is not None else []
    return {
        "dataset":"locomo_refined_public","family":"LoCoMo-Refined","split":"public",
        "example_id":f"locomo_refined_public:{qid}","conversation_id":str(sample_id) if sample_id is not None else None,
        "question_id":qid,"question":str(raw.get("question","")),"answer":answer_value,
        "gold_evidence":evidence,"conversation":[],"task_type":task,
        "metadata":{"conversation_idx":raw.get("conversation_idx"),"qa_index":raw.get("qa_index"),"raw":raw,"normalization":"locomo_refined_v1"}
    }
