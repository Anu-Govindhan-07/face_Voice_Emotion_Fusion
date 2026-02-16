from __future__ import annotations


def build_track_label(summary: dict) -> str:
    name = summary.get("resolved_name") or "Unknown"
    emotion = summary.get("current_emotion", {}).get("emotion", "neutral")
    return f"{name} | {emotion}"
