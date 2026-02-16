from __future__ import annotations

from pathlib import Path


def transcribe_audio(audio_path: Path) -> list[dict]:
    """Timestamped multilingual transcript stub."""
    _ = audio_path
    return [
        {"start": 0.0, "end": 2.0, "text": "Hello, I'm Anu", "speaker_id": "Speaker 1"},
        {"start": 3.2, "end": 5.6, "text": "Nice to meet you", "speaker_id": "Speaker 2"},
    ]
