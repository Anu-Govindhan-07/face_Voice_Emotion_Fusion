from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def extract_audio(video_path: Path, out_wav: Path) -> Path:
    """Extract mono wav audio if ffmpeg exists; otherwise create an empty placeholder file."""
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-ac",
            "1",
            "-ar",
            "16000",
            str(out_wav),
        ]
        subprocess.run(cmd, check=False, capture_output=True)
    if not out_wav.exists():
        out_wav.write_bytes(b"")
    return out_wav
