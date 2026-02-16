from src.names.speaker_face_map import map_speakers_to_faces


def test_maps_to_best_visible_track():
    diarization = [{"start": 0.0, "end": 2.0, "speaker_id": "Speaker 1"}]
    tracks = [
        {
            "track_id": "track_001",
            "bboxes": [
                {"ts": 0.5, "bbox": [0, 0, 100, 100]},
                {"ts": 1.0, "bbox": [0, 0, 100, 100]},
            ],
        },
        {
            "track_id": "track_002",
            "bboxes": [
                {"ts": 0.5, "bbox": [0, 0, 220, 220]},
                {"ts": 1.0, "bbox": [0, 0, 220, 220]},
            ],
        },
    ]
    mapping = map_speakers_to_faces(diarization, tracks)
    assert mapping["Speaker 1"]["track_id"] == "track_002"


def test_low_confidence_returns_unresolved():
    diarization = [{"start": 0.0, "end": 1.0, "speaker_id": "Speaker 1"}]
    tracks = [{"track_id": "track_001", "bboxes": []}]
    mapping = map_speakers_to_faces(diarization, tracks, min_confidence=0.3)
    assert mapping["Speaker 1"]["track_id"] is None
    assert mapping["Speaker 1"]["resolved"] is False
