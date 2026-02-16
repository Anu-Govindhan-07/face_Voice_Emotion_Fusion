from __future__ import annotations

from collections import Counter

EMOTIONS = ["neutral", "happy", "sad", "angry", "surprise"]


def infer_track_emotions(tracks: list[dict], interval_s: float = 0.5) -> list[dict]:
    """Mockable emotion inference interface for vit-face-expression."""
    out: list[dict] = []
    for track in tracks:
        samples = []
        ts = track["start_ts"]
        while ts <= track["end_ts"] + 1e-9:
            idx = int((ts * 10 + len(track["track_id"])) % len(EMOTIONS))
            conf = round(0.55 + (idx * 0.07), 3)
            samples.append({"ts": round(ts, 3), "emotion": EMOTIONS[idx], "confidence": min(conf, 0.99)})
            ts += interval_s
        counts = Counter(s["emotion"] for s in samples)
        dominant = counts.most_common(1)[0][0] if samples else "neutral"
        out.append({"track_id": track["track_id"], "samples": samples, "dominant_emotion": dominant})
    return out
