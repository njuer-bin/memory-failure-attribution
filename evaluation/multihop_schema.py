"""Schema and validation helpers for multi-hop gold evidence.

This module deliberately separates evidence count from hop count. Multiple
supporting evidence items do not imply a multi-hop reasoning chain.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


VALID_HOP_TYPES = {"single", "multi_hop", "temporal", "causal", "entity", "unknown"}


@dataclass(frozen=True)
class EvidenceNode:
    """One benchmark evidence item identified by stable provenance."""

    evidence_id: str
    text: str = ""
    session_index: Optional[int] = None
    message_index: Optional[int] = None


@dataclass(frozen=True)
class EvidenceRelation:
    """A directed relation between two evidence nodes."""

    source: str
    target: str
    relation: str
    order: int = 0


@dataclass
class MultiHopGoldEvidence:
    """Gold structure required to diagnose evidence-composition failures."""

    question_id: str
    question: str
    reference_answer: str
    gold_evidence: List[EvidenceNode] = field(default_factory=list)
    hop_count: int = 1
    hop_type: str = "unknown"
    ordered_path: List[str] = field(default_factory=list)
    relations: List[EvidenceRelation] = field(default_factory=list)
    bridge_evidence: List[str] = field(default_factory=list)
    annotation_status: str = "unreviewed"
    notes: str = ""

    def validate(self) -> List[str]:
        """Return validation errors without silently repairing annotations."""
        errors: List[str] = []
        node_ids = {node.evidence_id for node in self.gold_evidence}

        if not self.question_id:
            errors.append("question_id is required")
        if self.hop_count < 1:
            errors.append("hop_count must be >= 1")
        if self.hop_type not in VALID_HOP_TYPES:
            errors.append(f"invalid hop_type: {self.hop_type}")

        if self.ordered_path:
            unknown = [x for x in self.ordered_path if x not in node_ids]
            if unknown:
                errors.append(f"ordered_path contains unknown evidence ids: {unknown}")

        if self.bridge_evidence:
            unknown = [x for x in self.bridge_evidence if x not in node_ids]
            if unknown:
                errors.append(f"bridge_evidence contains unknown evidence ids: {unknown}")

        for relation in self.relations:
            if relation.source not in node_ids:
                errors.append(f"relation source not found: {relation.source}")
            if relation.target not in node_ids:
                errors.append(f"relation target not found: {relation.target}")

        if self.hop_count == 1 and len(self.ordered_path) > 2:
            errors.append("hop_count=1 cannot have an evidence path longer than two nodes")

        if self.hop_count > 1 and len(self.ordered_path) < 2:
            errors.append("multi-hop annotation requires an ordered_path with >= 2 nodes")

        return errors

    @property
    def is_multi_hop(self) -> bool:
        return self.hop_count > 1 or self.hop_type == "multi_hop"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "question": self.question,
            "reference_answer": self.reference_answer,
            "gold_evidence": [node.__dict__ for node in self.gold_evidence],
            "hop_count": self.hop_count,
            "hop_type": self.hop_type,
            "ordered_path": list(self.ordered_path),
            "relations": [relation.__dict__ for relation in self.relations],
            "bridge_evidence": list(self.bridge_evidence),
            "annotation_status": self.annotation_status,
            "notes": self.notes,
        }


def from_locomo_record(record: Dict[str, Any]) -> MultiHopGoldEvidence:
    """Create an *unreviewed* annotation from an existing LoCoMo record.

    The loader copies benchmark evidence/provenance only. It intentionally does
    not infer hop_count, relations, ordered_path, or bridge evidence.
    """
    evidence_items = record.get("evidence_messages") or []
    nodes: List[EvidenceNode] = []

    for index, item in enumerate(evidence_items):
        if isinstance(item, dict):
            evidence_id = str(item.get("id") or item.get("evidence_id") or f"evidence_{index}")
            text = str(item.get("text") or item.get("content") or "")
            session_index = item.get("session_index")
            message_index = item.get("message_index")
        else:
            evidence_id = str(item)
            text = ""
            session_index = None
            message_index = None
        nodes.append(
            EvidenceNode(
                evidence_id=evidence_id,
                text=text,
                session_index=session_index,
                message_index=message_index,
            )
        )

    return MultiHopGoldEvidence(
        question_id=str(record.get("question_id") or record.get("id") or ""),
        question=str(record.get("question") or ""),
        reference_answer=str(record.get("answer") or record.get("reference_answer") or ""),
        gold_evidence=nodes,
        annotation_status="unreviewed",
    )
