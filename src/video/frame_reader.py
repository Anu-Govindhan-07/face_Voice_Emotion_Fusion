from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class Frame:
    ts: float
    image: object | None


def iter_frames(video_path: Path, interval_s: float = 0.5) -> Iterator[Frame]:
    """Placeholder frame iterator. In production replace with cv2/video reader."""
    _ = video_path
    ts = 0.0
    for _ in range(20):
        yield Frame(ts=round(ts, 3), image=None)
        ts += interval_s
