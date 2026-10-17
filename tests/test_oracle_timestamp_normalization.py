from datetime import datetime, timezone

from experiments.run_oracle_experiments import _msg, _timestamp_ms


def test_locomo_human_readable_timestamp_is_preserved_as_epoch_milliseconds():
    role, text, timestamp = _msg({
        "role": "Caroline",
        "content": "I went to a LGBTQ support group yesterday.",
        "timestamp": "1:56 pm on 8 May, 2023",
    })

    expected = int(datetime(2023, 5, 8, 13, 56, tzinfo=timezone.utc).timestamp() * 1000)
    assert role == "Caroline"
    assert text == "I went to a LGBTQ support group yesterday."
    assert timestamp == expected


def test_timestamp_normalizer_accepts_iso_datetime_and_epoch_seconds():
    iso = _timestamp_ms("2023-05-25T13:14:00Z")
    seconds = int(datetime(2023, 5, 25, 13, 14, tzinfo=timezone.utc).timestamp())

    assert iso == seconds * 1000
    assert _timestamp_ms(seconds) == seconds * 1000


def test_unrecognized_timestamp_is_not_fabricated():
    assert _timestamp_ms("not a date") is None


def test_session_level_date_is_preserved_for_message_timestamp_fallback():
    from experiments.run_oracle_experiments import _sessions

    sessions = _sessions({
        "conversation": [{
            "session_id": "D2",
            "date": "1:14 pm on 25 May, 2023",
            "messages": [{"speaker": "Melanie", "text": "I ran a charity race last Saturday."}],
        }]
    })

    assert sessions[0]["date"] == "1:14 pm on 25 May, 2023"
