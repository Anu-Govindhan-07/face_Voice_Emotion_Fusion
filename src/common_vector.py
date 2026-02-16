from __future__ import annotations

import json
import math
from pathlib import Path
import random


def deterministic_vector(key: str, dim: int = 512) -> list[float]:
    rng = random.Random(abs(hash(key)) % (2**32))
    vec = [rng.gauss(0, 1) for _ in range(dim)]
    return normalize(vec)


def normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return dot(normalize(a), normalize(b))


def save_vector(path: Path, vec: list[float]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(vec), encoding='utf-8')
    return str(path)


def load_vector(path: Path) -> list[float]:
    return json.loads(path.read_text(encoding='utf-8'))
