from pathlib import Path

from src.common_vector import normalize
from src.identity.enroll import enroll_identity
from src.identity.match import match_embedding
from src.identity.store import IdentityStore


def test_enroll_updates_json_and_embedding_saved(tmp_path: Path):
    store = IdentityStore(tmp_path / "identity_store")
    emb = normalize([1.0] * 16)
    identity = enroll_identity(store, "Anu", emb, "job1", "track_001")

    assert identity["name"] == "Anu"
    payload = store.load()
    assert len(payload["identities"]) == 1
    emb_path = Path(payload["identities"][0]["embeddings"][0])
    assert emb_path.exists()


def test_match_thresholds(tmp_path: Path):
    store = IdentityStore(tmp_path / "identity_store")
    emb = normalize([1.0] * 16)
    enroll_identity(store, "Anu", emb, "job1", "track_001")

    matched = match_embedding(store, emb, match_threshold=0.9, maybe_threshold=0.7)
    assert matched["status"] == "matched"

    maybe_vec = normalize([1.0] * 8 + [-1.0] * 8)
    maybe = match_embedding(store, maybe_vec, match_threshold=0.95, maybe_threshold=0.1)
    assert maybe["status"] in {"maybe", "unknown"}

    unknown = match_embedding(store, [-x for x in emb], match_threshold=0.8, maybe_threshold=0.2)
    assert unknown["status"] == "unknown"
