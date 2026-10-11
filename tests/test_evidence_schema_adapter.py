from evaluation.answer_semantic_eval import _evidence_content, _joined_evidence


def test_evidence_content_accepts_trace_text_schema():
    evidence = {"text": "Caroline is interested in counseling."}
    assert _evidence_content(evidence) == "Caroline is interested in counseling."


def test_evidence_content_prefers_content_schema():
    evidence = {
        "content": "retrieval artifact text",
        "text": "trace text",
    }
    assert _evidence_content(evidence) == "retrieval artifact text"


def test_joined_evidence_does_not_drop_trace_text():
    evidence = [
        {"text": "Caroline attended an LGBTQ support group."},
        {"content": "She found it powerful."},
    ]
    joined = _joined_evidence(evidence)
    assert "Caroline attended an LGBTQ support group." in joined
    assert "She found it powerful." in joined
