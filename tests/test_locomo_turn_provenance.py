"""Regression tests for LoCoMo-to-MemoryEngine turn provenance alignment."""
from datasets.adapters import _locomo_turns


def test_locomo_turn_ids_follow_ingested_nonempty_message_index():
    conversation = {
        "conversation": [
            {
                "session_id": "session_1",
                "messages": [
                    {"dia_id": "D1", "text": "first turn"},
                    {"dia_id": "D2", "text": ""},
                    {"dia_id": "D3", "text": "third source item"},
                    {"dia_id": "D4", "text": "   "},
                    {"dia_id": "D5", "text": "last turn"},
                ],
            }
        ]
    }

    turns = _locomo_turns(conversation)

    # MemoryEngine only receives non-empty messages, so its counter has no gaps.
    assert [turn["turn_id"] for turn in turns] == [
        "session_1:turn_0",
        "session_1:turn_1",
        "session_1:turn_2",
    ]
    # Keep benchmark IDs separately so evidence can still resolve via source IDs.
    assert [turn["benchmark_turn_id"] for turn in turns] == ["D1", "D3", "D5"]
    assert [turn["text"] for turn in turns] == [
        "first turn",
        "third source item",
        "last turn",
    ]


def test_locomo_turn_ids_reset_for_each_session():
    conversation = {
        "conversation": [
            {"session_id": "session_1", "messages": [{"text": "one"}]},
            {"session_id": "session_2", "messages": [{"text": "two"}, {"text": "three"}]},
        ]
    }

    turns = _locomo_turns(conversation)

    assert [turn["turn_id"] for turn in turns] == [
        "session_1:turn_0",
        "session_2:turn_0",
        "session_2:turn_1",
    ]
