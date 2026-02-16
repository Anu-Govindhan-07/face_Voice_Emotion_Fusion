from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JobContext:
    job_id: str
    video_path: Path
    job_root: Path
    input_dir: Path
    output_dir: Path
    embedding_dir: Path


    @classmethod
    def build(cls, job_id: str, video_path: str | Path, base_dir: str | Path = "data/jobs") -> "JobContext":
        video = Path(video_path)
        job_root = Path(base_dir) / job_id
        return cls(
            job_id=job_id,
            video_path=video,
            job_root=job_root,
            input_dir=job_root / "input",
            output_dir=job_root / "outputs",
            embedding_dir=job_root / "embeddings" / "face",
        )
