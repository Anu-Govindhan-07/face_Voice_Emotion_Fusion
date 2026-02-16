from __future__ import annotations

from pathlib import Path


def diarize_audio(audio_path: Path) -> list[dict]:
    """Returns speaker segments. Replace with pyannote or equivalent in production."""
    _ = audio_path
    return [
        {"start": 0.0, "end": 3.0, "speaker_id": "Speaker 1"},
        {"start": 3.0, "end": 6.0, "speaker_id": "Speaker 2"},
    ]
