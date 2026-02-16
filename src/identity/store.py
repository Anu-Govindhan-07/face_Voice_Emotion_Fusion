from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IdentityStore:
    root: Path

    @property
    def json_path(self) -> Path:
        return self.root / "identities.json"

    @property
    def embeddings_dir(self) -> Path:
        return self.root / "embeddings"

    def load(self) -> dict:
        self.root.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        if not self.json_path.exists():
            self.save({"identities": []})
        return json.loads(self.json_path.read_text(encoding="utf-8"))

    def save(self, payload: dict) -> None:
        self.json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def next_id(self, payload: dict) -> str:
        existing = [int(item["id"]) for item in payload.get("identities", []) if str(item.get("id", "")).isdigit()]
        return f"{(max(existing) + 1) if existing else 1:04d}"

    def add_or_update_identity(self, name: str, embedding_file: str, source: dict) -> dict:
        payload = self.load()
        now = _now_iso()
        for identity in payload["identities"]:
            if identity["name"].lower() == name.lower():
                identity["embeddings"].append(embedding_file)
                identity["sources"].append(source)
                identity["last_seen_at"] = now
                self.save(payload)
                return identity

        identity = {
            "id": self.next_id(payload),
            "name": name,
            "embeddings": [embedding_file],
            "created_at": now,
            "last_seen_at": now,
            "sources": [source],
        }
        payload["identities"].append(identity)
        self.save(payload)
        return identity
