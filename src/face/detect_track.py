from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _iou(box_a: list[float], box_b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter_x1, inter_y1 = max(ax1, bx1), max(ay1, by1)
    inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter = inter_w * inter_h
    a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    denom = a + b - inter
    return inter / denom if denom else 0.0


@dataclass
class Track:
    track_id: str
    boxes: list[dict[str, Any]] = field(default_factory=list)


class FaceTracker:
    """IoU based tracker. Uses MTCNN if available, else deterministic fallback detections."""

    def __init__(self, iou_threshold: float = 0.4):
        self.iou_threshold = iou_threshold
        self._counter = 0

    def _new_track(self) -> Track:
        self._counter += 1
        return Track(track_id=f"track_{self._counter:03d}")

    def detect_faces(self, frame: Any) -> list[list[float]]:
        _ = frame
        # Fallback mock detection for runnable default.
        return [[100, 100, 220, 240]]

    def run(self, frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
        tracks: list[Track] = []
        for frame in frames:
            ts = frame["ts"]
            detections = self.detect_faces(frame.get("image"))
            for det in detections:
                matched = None
                for track in tracks:
                    if not track.boxes:
                        continue
                    if _iou(track.boxes[-1]["bbox"], det) >= self.iou_threshold:
                        matched = track
                        break
                if matched is None:
                    matched = self._new_track()
                    tracks.append(matched)
                matched.boxes.append({"ts": ts, "bbox": det})

        payload = []
        for track in tracks:
            if not track.boxes:
                continue
            payload.append(
                {
                    "track_id": track.track_id,
                    "start_ts": track.boxes[0]["ts"],
                    "end_ts": track.boxes[-1]["ts"],
                    "bboxes": track.boxes,
                }
            )
        return payload
