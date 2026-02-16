from __future__ import annotations

from pathlib import Path


from src.audio.diarize import diarize_audio
from src.audio.transcribe import transcribe_audio
from src.emotion.infer import infer_track_emotions
from src.face.detect_track import FaceTracker
from src.face.embed import FaceEmbedder
from src.identity.enroll import enroll_identity
from src.identity.match import match_embedding
from src.identity.store import IdentityStore
from src.names.name_extraction import extract_name_signals
from src.names.speaker_face_map import map_speakers_to_faces
from src.pipeline.artifacts import ensure_job_dirs, write_json
from src.pipeline.job_context import JobContext


def _load_config(path: str | Path = "config/default.yaml") -> dict:
    default = {
        "interval_seconds": 0.5,
        "identity": {"match_threshold": 0.72, "maybe_threshold": 0.58},
        "name_detection": {"self_intro_confidence": 0.9, "mention_confidence": 0.75},
        "speaker_face": {"min_visibility_confidence": 0.25},
    }
    try:
        import yaml  # type: ignore

        return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return default


def run_job(video_path: str, job_id: str, config_path: str | Path = "config/default.yaml") -> dict:
    cfg = _load_config(config_path)
    ctx = JobContext.build(job_id=job_id, video_path=video_path)
    ensure_job_dirs(ctx)

    frames = [{"ts": round(i * cfg["interval_seconds"], 3), "image": None} for i in range(20)]
    tracks = FaceTracker().run(frames)
    write_json(ctx.output_dir / "face_tracks.json", tracks)

    embedder = FaceEmbedder()
    track_embeddings: dict[str, list[float]] = {}
    for track in tracks:
        emb = embedder.aggregate_track_embedding(track)
        track_embeddings[track["track_id"]] = emb
        embedder.save_embedding(emb, ctx.embedding_dir / f"{track['track_id']}.npy")

    emotions = infer_track_emotions(tracks, interval_s=cfg["interval_seconds"])
    write_json(ctx.output_dir / "emotions.json", emotions)

    from src.video.extract_audio import extract_audio

    audio_path = extract_audio(Path(video_path), ctx.input_dir / "audio.wav")
    diarization = diarize_audio(audio_path)
    transcript = transcribe_audio(audio_path)
    write_json(ctx.output_dir / "diarization.json", diarization)
    write_json(ctx.output_dir / "transcript.json", transcript)

    name_signals = extract_name_signals(transcript)
    write_json(ctx.output_dir / "name_signals.json", name_signals)

    speaker_map = map_speakers_to_faces(
        diarization=diarization,
        tracks=tracks,
        min_confidence=cfg["speaker_face"]["min_visibility_confidence"],
    )

    track_name_candidates: dict[str, dict] = {}
    for item in name_signals:
        speaker_id = item["speaker_id"]
        mapped = speaker_map.get(speaker_id, {})
        track_id = mapped.get("track_id")
        if not track_id:
            continue
        for signal in item.get("signals", []):
            if signal["type"] == "self" and signal["confidence"] >= cfg["name_detection"]["self_intro_confidence"]:
                track_name_candidates[track_id] = signal

    store = IdentityStore(Path("identity_store"))
    associations = []
    for track in tracks:
        tid = track["track_id"]
        embedding = track_embeddings[tid]
        match = match_embedding(
            store,
            embedding,
            match_threshold=cfg["identity"]["match_threshold"],
            maybe_threshold=cfg["identity"]["maybe_threshold"],
        )

        enrolled = None
        if tid in track_name_candidates:
            signal = track_name_candidates[tid]
            enrolled = enroll_identity(store, signal["name"], embedding, job_id, tid)

        associations.append(
            {
                "track_id": tid,
                "speaker_mapping": next(({"speaker_id": spk, **val} for spk, val in speaker_map.items() if val.get("track_id") == tid), None),
                "name_signal": track_name_candidates.get(tid),
                "identity_match": match,
                "enrolled_identity": enrolled,
            }
        )

    write_json(ctx.output_dir / "associations.json", associations)

    emotion_by_track = {item["track_id"]: item for item in emotions}
    final_summary = []
    for assoc in associations:
        track_id = assoc["track_id"]
        e = emotion_by_track.get(track_id, {"samples": [], "dominant_emotion": "neutral"})
        current = e["samples"][-1] if e["samples"] else {"emotion": "neutral", "confidence": 0.0, "ts": None}
        match = assoc["identity_match"]
        resolved_name = None
        if match.get("status") == "matched" and match.get("identity"):
            resolved_name = match["identity"]["name"]
        elif assoc.get("name_signal"):
            resolved_name = assoc["name_signal"]["name"]

        final_summary.append(
            {
                "track_id": track_id,
                "mapped_speaker_id": assoc.get("speaker_mapping", {}).get("speaker_id") if assoc.get("speaker_mapping") else None,
                "detected_name": assoc.get("name_signal", {}).get("name") if assoc.get("name_signal") else None,
                "recognized_identity": {
                    "status": match.get("status"),
                    "score": match.get("score"),
                    "identity_id": match.get("identity", {}).get("id") if match.get("identity") else None,
                    "identity_name": match.get("identity", {}).get("name") if match.get("identity") else None,
                },
                "dominant_emotion": e.get("dominant_emotion"),
                "current_emotion": current,
                "resolved_name": resolved_name or "Unknown",
            }
        )

    write_json(ctx.output_dir / "final_track_summary.json", final_summary)
    return {"job_id": job_id, "outputs": str(ctx.output_dir)}
