from datasets.adapters import _locomo_evidence, _locomo_sessions, _locomo_turns


def test_locomo_turn_ids_skip_empty_messages_deterministically():
    conversation = {
        "sessions": [
            {
                "messages": [
                    {"dia_id": "D1:0", "speaker": "A", "text": ""},
                    {"dia_id": "D1:1", "speaker": "A", "text": "first"},
                    {"dia_id": "D1:2", "speaker": "B", "text": "second"},
                ]
            }
        ]
    }

    sessions = _locomo_sessions(conversation)
    turns = _locomo_turns(sessions)

    assert [x["turn_id"] for x in turns] == ["D1:turn_0", "D1:turn_1"]
    assert [x["benchmark_turn_id"] for x in turns] == ["D1:1", "D1:2"]
    assert [x["text"] for x in turns] == ["first", "second"]


def test_locomo_gold_evidence_maps_benchmark_dia_id_to_engine_turn():
    conversation = {
        "sessions": [
            {
                "messages": [
                    {"dia_id": "D1:0", "speaker": "A", "text": "alpha"},
                    {"dia_id": "D1:1", "speaker": "B", "text": "target evidence"},
                ]
            }
        ]
    }

    sessions = _locomo_sessions(conversation)
    evidence = _locomo_evidence(
        [{"evidence_id": "e1", "dia_id": "D1:1", "text": "target evidence"}],
        example_id="q",
        conversation=sessions,
    )

    assert evidence == [
        {
            "evidence_id": "e1",
            "source_id": "D1",
            "turn_id": "D1:turn_1",
            "timestamp": None,
            "text": "target evidence",
            "role": "B",
            "granularity": "turn",
        }
    ]


def test_locomo_gold_evidence_does_not_accept_unknown_turn_as_resolved():
    conversation = {
        "sessions": [
            {"messages": [{"dia_id": "D1:0", "speaker": "A", "text": "alpha"}]}
        ]
    }

    sessions = _locomo_sessions(conversation)
    evidence = _locomo_evidence(
        [{"evidence_id": "e1", "dia_id": "D1:99", "text": "not present"}],
        example_id="q",
        conversation=sessions,
    )

    assert evidence[0]["granularity"] == "unresolved"
    assert evidence[0]["turn_id"] == "D1:99"
