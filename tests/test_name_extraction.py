from src.names.name_extraction import extract_name_signals


def _first_signals(text: str):
    result = extract_name_signals([
        {"start": 0.0, "end": 1.0, "speaker_id": "Speaker 1", "text": text}
    ])
    return result[0]["signals"]


def test_extract_multiple_self_names_english():
    signals = _first_signals("Hello, I'm Matthew and Sina")
    assert { (s["name"], s["type"]) for s in signals } == {("Matthew", "self"), ("Sina", "self")}


def test_extract_mentioned_name():
    signals = _first_signals("This is Taylor")
    assert { (s["name"], s["type"]) for s in signals } == {("Taylor", "mentioned")}


def test_extract_swedish_self_intro():
    signals = _first_signals("Jag heter Anu")
    assert { (s["name"], s["type"]) for s in signals } == {("Anu", "self")}


def test_no_false_positive_accountable():
    signals = _first_signals("I'm accountable to myself")
    assert signals == []
