from __future__ import annotations


def build_ui_payload(
    face_tracks: list[dict],
    diarization: list[dict],
    emotions: list[dict],
    associations: list[dict],
    final_summary: list[dict],
) -> dict:
    matched = sum(1 for row in final_summary if row.get("recognized_identity", {}).get("status") == "matched")
    emotion_by_track = {item.get("track_id"): item.get("samples", []) for item in emotions}
    return {
        "summary": {
            "face_tracks": len(face_tracks),
            "speaker_segments": len(diarization),
            "identities_matched": matched,
            "emotion_tracks": len(emotions),
            "associations": len(associations),
        },
        "face_tracks": face_tracks,
        "tracks": final_summary,
        "emotion_samples": emotion_by_track,
    }
