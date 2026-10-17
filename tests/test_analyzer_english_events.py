"""Regression tests for common English event expressions in Parse-2."""

from memory_engine.analyzer import MemoryAnalyzer


def _events(text: str):
    return MemoryAnalyzer().analyze(
        user_id="locomo-test",
        content=text,
        timestamp=1_700_000_000_000,
        source="user",
        source_raw_id="raw-test",
        source_session_id="D1",
        source_turn_id="D1:turn_2",
    )["events"]


def test_went_to_support_group_is_preserved_as_event_with_provenance():
    text = "I went to a LGBTQ support group yesterday and it was so powerful."
    events = _events(text)

    assert len(events) == 1
    assert events[0].content == text
    assert events[0].source_session_id == "D1"
    assert events[0].source_turn_id == "D1:turn_2"
    assert events[0].source_raw_id == "raw-test"


def test_ran_a_charity_race_is_preserved_as_event_with_provenance():
    text = "Melanie ran a charity race last Saturday for mental health."
    events = _events(text)

    assert len(events) == 1
    assert events[0].content == text
    assert events[0].source_turn_id == "D1:turn_2"


def test_unrelated_counselor_message_does_not_create_event_from_paint_question():
    # The question mentions painting, but this evidence text does not.
    text = "You'd be a great counselor! Your empathy and understanding will really help the people you work with. By the way, take a look at this."
    assert _events(text) == []
