from src.ui.build_ui_json import build_ui_payload


def test_build_ui_payload_counts():
    payload = build_ui_payload(
        face_tracks=[{"track_id": "track_1"}, {"track_id": "track_2"}],
        diarization=[{"speaker_id": "Speaker 1"}],
        emotions=[{"track_id": "track_1"}, {"track_id": "track_2"}],
        associations=[{"track_id": "track_1"}],
        final_summary=[
            {"track_id": "track_1", "recognized_identity": {"status": "matched"}},
            {"track_id": "track_2", "recognized_identity": {"status": "unknown"}},
        ],
    )
    assert payload["summary"]["face_tracks"] == 2
    assert payload["summary"]["identities_matched"] == 1
