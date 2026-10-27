from experiments.analyze_gate_confusion import analyze


def test_confusion_polarity_is_explicit():
    key = {
        "locomo-001": {"gate_status": "insufficient"},  # human insufficient -> tp
        "locomo-002": {"gate_status": "insufficient"},  # human sufficient   -> fp
        "locomo-003": {"gate_status": "sufficient"},    # human insufficient -> fn (missed)
        "locomo-004": {"gate_status": "sufficient"},    # human sufficient   -> tn
    }
    adj = {
        "locomo-001": {"adj_evidence_sufficient": "False"},
        "locomo-002": {"adj_evidence_sufficient": "True"},
        "locomo-003": {"adj_evidence_sufficient": "False"},
        "locomo-004": {"adj_evidence_sufficient": "True"},
    }
    result = analyze(key, adj)["overall"]
    assert result["tp_both_insufficient"] == 1
    assert result["fp_gate_insufficient_human_sufficient"] == 1
    assert result["fn_gate_sufficient_human_insufficient"] == 1
    assert result["tn_both_sufficient"] == 1
    assert result["missed_truly_insufficient"] == 1
    assert result["falsely_called_insufficient"] == 1
