from __future__ import annotations

from pathlib import Path

from src.common_vector import cosine_similarity, load_vector

from .store import IdentityStore


def match_embedding(
    store: IdentityStore,
    embedding: list[float],
    match_threshold: float = 0.72,
    maybe_threshold: float = 0.58,
) -> dict:
    payload = store.load()
    best = {"status": "unknown", "score": 0.0, "identity": None}

    for identity in payload.get("identities", []):
        for emb_path in identity.get("embeddings", []):
            path = Path(emb_path)
            if not path.exists():
                continue
            ref = load_vector(path)
            score = cosine_similarity(embedding, ref)
            if score > best["score"]:
                best = {"status": "unknown", "score": score, "identity": identity}

    if best["identity"] is None:
        return best
    if best["score"] >= match_threshold:
        best["status"] = "matched"
    elif best["score"] >= maybe_threshold:
        best["status"] = "maybe"
    else:
        best["status"] = "unknown"
    best["score"] = round(best["score"], 4)
    return best
