from __future__ import annotations

from .store import IdentityStore
from src.common_vector import save_vector


def enroll_identity(
    store: IdentityStore,
    name: str,
    embedding: list[float],
    job_id: str,
    track_id: str,
) -> dict:
    filename = f"{name.lower().replace(' ', '_')}_{job_id}_{track_id}.npy"
    path = store.embeddings_dir / filename
    save_vector(path, embedding)
    source = {"job_id": job_id, "track_id": track_id}
    return store.add_or_update_identity(name=name, embedding_file=str(path), source=source)
