"""Compatibility re-export.

The single implementation of failure attribution lives in
``evaluation.attribution`` (one protocol, one category enum, non-circular
evidence-sufficiency gate). This module re-exports it for existing callers.
"""
from evaluation.attribution import (
    E0_EVIDENCE_INSUFFICIENT,
    EVAL_SEMANTIC_UNCERTAIN,
    F1_FORMATION,
    F2_STORAGE,
    F3_EVOLUTION,
    F4_RETRIEVAL,
    F5_CONTEXT,
    F6_REASONING_CANDIDATE,
    RC_REASONING_CONTROL_FAILURE,
    attribute_failure,
    evidence_sufficiency_gate,
    first_missing_stage,
)

__all__ = [
    "attribute_failure",
    "evidence_sufficiency_gate",
    "first_missing_stage",
    "E0_EVIDENCE_INSUFFICIENT",
    "EVAL_SEMANTIC_UNCERTAIN",
    "F1_FORMATION", "F2_STORAGE", "F3_EVOLUTION", "F4_RETRIEVAL", "F5_CONTEXT",
    "F6_REASONING_CANDIDATE",
    "RC_REASONING_CONTROL_FAILURE",
]
