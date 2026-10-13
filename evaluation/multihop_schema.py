"""Schema and validation helpers for multi-hop gold evidence.

The schema deliberately separates evidence *structure* from hop type. Multiple
supporting evidence items can form an aggregation without forming a relational
multi-hop chain.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


VALID_HOP_TYPES = {"single", "multi_hop", "temporal", "causal", "entity", "unknown"}
VALID_EVIDENCE_STRUCTURES = {"single", "chain", "aggregation", "uncertain"}


@dataclass(frozen=True)
class EvidenceNode:
    evidence_id: str
    text: str = ""
    session_index: Optional[int] = None
    message_index: Optional[int] = None


@dataclass(frozen=True)
class EvidenceRelation:
    source: str
    target: str
    relation: str
    order: int = 0


@dataclass
class MultiHopGoldEvidence:
    """Gold structure for diagnosing evidence-composition failures.

    ``chain`` is a relational/co-reference/causal/temporal path. ``aggregation``
    means multiple independent evidence items are jointly required for an
    enumeration/counting/set-style answer.
    """

    question_id: str
    question: str
    reference_answer: str
    gold_evidence: List[EvidenceNode] = field(default_factory=list)
    hop_count: int = 1
    hop_type: str = "unknown"
    evidence_structure: str = "uncertain"
    ordered_path: List[str] = field(default_factory=list)
    relations: List[EvidenceRelation] = field(default_factory=list)
    bridge_evidence: List[str] = field(default_factory=list)
    annotation_status: str = "unreviewed"
    notes: str = ""

    def validate(self) -> List[str]:
        errors: List[str] = []
        node_ids = {node.evidence_id for node in self.gold_evidence}
        if not self.question_id:
            errors.append("question_id is required")
        if self.hop_count < 1:
            errors.append("hop_count must be >= 1")
        if self.hop_type not in VALID_HOP_TYPES:
            errors.append(f"invalid hop_type: {self.hop_type}")
        if self.evidence_structure not in VALID_EVIDENCE_STRUCTURES:
            errors.append(f"invalid evidence_structure: {self.evidence_structure}")

        unknown = [x for x in self.ordered_path if x not in node_ids]
        if unknown:
            errors.append(f"ordered_path contains unknown evidence ids: {unknown}")
        unknown = [x for x in self.bridge_evidence if x not in node_ids]
        if unknown:
            errors.append(f"bridge_evidence contains unknown evidence ids: {unknown}")
        for relation in self.relations:
            if relation.source not in node_ids:
                errors.append(f"relation source not found: {relation.source}")
            if relation.target not in node_ids:
                errors.append(f"relation target not found: {relation.target}")

        if self.evidence_structure == "chain":
            if len(self.ordered_path) < 2:
                errors.append("chain annotation requires an ordered_path with >= 2 nodes")
            if self.hop_count < 2:
                errors.append("chain annotation requires hop_count >= 2")
        elif self.evidence_structure == "aggregation":
            if len(self.gold_evidence) < 2:
                errors.append("aggregation annotation requires >= 2 evidence items")
            if self.ordered_path:
                errors.append("aggregation should not use an ordered relational path")
            if self.bridge_evidence:
                errors.append("aggregation should not use bridge_evidence")
        elif self.evidence_structure == "single":
            if self.hop_count != 1:
                errors.append("single structure requires hop_count=1")
            if len(self.ordered_path) > 1:
                errors.append("single structure cannot have a relational path")
        elif self.evidence_structure == "uncertain":
            pass

        if self.hop_count == 1 and len(self.ordered_path) > 2:
            errors.append("hop_count=1 cannot have an evidence path longer than two nodes")
        if self.hop_count > 1 and len(self.ordered_path) < 2 and self.evidence_structure != "aggregation":
            errors.append("multi-hop annotation requires an ordered_path with >= 2 nodes")
        return errors

    @property
    def is_multi_hop(self) -> bool:
        """True only for relational multi-hop chains, not aggregations."""
        return self.evidence_structure == "chain"

    @property
    def is_aggregation(self) -> bool:
        return self.evidence_structure == "aggregation"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "question": self.question,
            "reference_answer": self.reference_answer,
            "gold_evidence": [node.__dict__ for node in self.gold_evidence],
            "hop_count": self.hop_count,
            "hop_type": self.hop_type,
            "evidence_structure": self.evidence_structure,
            "ordered_path": list(self.ordered_path),
            "relations": [relation.__dict__ for relation in self.relations],
            "bridge_evidence": list(self.bridge_evidence),
            "annotation_status": self.annotation_status,
            "notes": self.notes,
        }


def from_locomo_record(record: Dict[str, Any]) -> MultiHopGoldEvidence:
    """Create an unreviewed annotation from LoCoMo evidence provenance only."""
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
        nodes.append(EvidenceNode(evidence_id, text, session_index, message_index))

    return MultiHopGoldEvidence(
        question_id=str(record.get("question_id") or record.get("id") or ""),
        question=str(record.get("question") or ""),
        reference_answer=str(record.get("answer") or record.get("reference_answer") or ""),
        gold_evidence=nodes,
        annotation_status="unreviewed",
    )
