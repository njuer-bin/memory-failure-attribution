from memory_engine.analyzer import MemoryAnalyzer


def test_locomo_english_evidence_cues_are_formed():
    analyzer = MemoryAnalyzer()
    cases = [
        ("Gonna continue my edu and check out career options, which is pretty exciting!", "continue my edu"),
        ("I'm keen on counseling or working in mental health - I'd love to support those with similar issues.", "interest"),
        ("Researching adoption agencies — it's been a dream to have a family.", "researching"),
        ("The transgender stories were so inspiring!", "transgender"),
        ("We're thinking about going camping next month.", "camping"),
        ("They've been there through everything after that tough breakup.", "breakup"),
        ("It'll be tough as a single parent, but I'm up for the challenge!", "single parent"),
    ]
    for content, cue in cases:
        result = analyzer.analyze(
            "u", content, 1,
            source_raw_id="raw-1", source_session_id="D1", source_turn_id="D1:turn_8",
        )
        memories = result["facts"] + result["relations"] + result["events"] + result["rules"] + result["profiles"]
        assert any(cue.lower() in m.content.lower() for m in memories), (content, cue, memories)
        assert any(m.source_turn_id == "D1:turn_8" for m in memories)


def test_interest_and_relationship_status_are_structured_without_inference():
    analyzer = MemoryAnalyzer()
    result = analyzer.analyze("u", "I'm keen on counseling or working in mental health.", 1,
                              source_turn_id="D1:turn_10")
    assert any(f.predicate == "interest" and "counseling" in f.object.lower() for f in result["facts"])

    result = analyzer.analyze("u", "I'm single.", 1, source_turn_id="D3:turn_12")
    assert any(f.predicate == "relationship_status" and f.object.lower() == "" for f in result["facts"]) is False
