from __future__ import annotations


def score_face_quality(bbox: list[float]) -> float:
    """Simple quality proxy using bbox area."""
    x1, y1, x2, y2 = bbox
    area = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    return min(1.0, area / 50000.0)
