from __future__ import annotations


def map_speakers_to_faces(diarization: list[dict], tracks: list[dict], min_confidence: float = 0.25) -> dict[str, dict]:
    mapping: dict[str, dict] = {}

    for seg in diarization:
        start, end, speaker_id = seg["start"], seg["end"], seg["speaker_id"]
        best_track = None
        best_score = 0.0

        for track in tracks:
            visible_frames = [
                b for b in track.get("bboxes", []) if start <= b["ts"] <= end
            ]
            if not visible_frames:
                continue
            presence = len(visible_frames) / max(1, len(track.get("bboxes", [])))
            avg_area = 0.0
            for frame in visible_frames:
                x1, y1, x2, y2 = frame["bbox"]
                avg_area += max(0.0, x2 - x1) * max(0.0, y2 - y1)
            avg_area /= len(visible_frames)
            area_score = min(1.0, avg_area / 50000.0)
            score = 0.6 * presence + 0.4 * area_score
            if score > best_score:
                best_score = score
                best_track = track["track_id"]

        mapping[speaker_id] = {
            "track_id": best_track if best_score >= min_confidence else None,
            "confidence": round(best_score, 3),
            "resolved": best_score >= min_confidence,
        }

    return mapping
