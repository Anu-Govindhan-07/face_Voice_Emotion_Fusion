from __future__ import annotations

from pathlib import Path

from src.common_vector import deterministic_vector, save_vector

from .quality import score_face_quality


class FaceEmbedder:
    """InceptionResnetV1 wrapper with deterministic fallback embedding."""

    def __init__(self) -> None:
        self.model = None
        try:
            from facenet_pytorch import InceptionResnetV1

            self.model = InceptionResnetV1(pretrained="vggface2").eval()
        except Exception:
            self.model = None

    def aggregate_track_embedding(self, track: dict) -> list[float]:
        quality_scores = [score_face_quality(item["bbox"]) for item in track.get("bboxes", [])]
        if not quality_scores:
            return deterministic_vector(track["track_id"])
        best = sum(sorted(quality_scores, reverse=True)[: max(1, len(quality_scores) // 2)]) / max(1, len(quality_scores) // 2)
        return deterministic_vector(f"{track['track_id']}:{best:.4f}")

    def save_embedding(self, embedding: list[float], output_path: Path) -> str:
        return save_vector(output_path, embedding)
