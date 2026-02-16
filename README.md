# Full Video Identity + Emotion Pipeline (JSON/.npy only)

This repository implements a full video workflow:

1. **Upload video**
2. **Face detect + track** (`facenet-pytorch` MTCNN interface, IoU tracking fallback)
3. **Face embeddings** (`InceptionResnetV1(pretrained="vggface2")` interface)
4. **Emotion inference every 0.5s** (`vit-face-expression` style interface with fallback)
5. **Audio extraction + diarization + transcription**
6. **Name detection** (language-aware, multilingual-friendly rules)
7. **Speaker ↔ face mapping**
8. **Identity matching/enrollment** to persistent JSON + `.npy` embeddings store
9. **Final track summary** + `ui.json` payload for the dashboard

> No SQL/DB is used. Persistent identity state is in `identity_store/identities.json` and `identity_store/embeddings/*.npy`.

## Repository Layout

- `src/main.py`: CLI entrypoint
- `src/pipeline/run_job.py`: orchestration
- `src/face/*`: detect, track, embed, quality
- `src/audio/*`: diarization/transcription interfaces
- `src/names/*`: language detection, name extraction, speaker-face mapping
- `src/identity/*`: JSON store, matching, enrollment
- `src/ui/*`: label helpers and `ui.json` payload builder
- `web/*`: dashboard UI (dark style matching the uploaded mock)
- `tests/*`: unit tests for names, matching, mapping

## Run (Linux / macOS)

```bash
python -m src.main --video /path/to/video.mp4 --job_id job_001
```

## Run on Windows

### PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main --video C:\videos\input.mp4 --job_id job_001
```

### CMD

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
python -m src.main --video C:\videos\input.mp4 --job_id job_001
```

## Dashboard UI (same style as requested)

1. Run the pipeline first:
   - `python -m src.main --video <video> --job_id <job_id>`
2. Start static server from repo root:
   - `python -m http.server 8080`
3. Open:
   - `http://localhost:8080/web/`
4. In UI:
   - Upload the video file in the top bar.
   - Click **Analyze** and pick `data/jobs/<job_id>/outputs/ui.json`.

The page renders:
- top metrics chips (face tracks / speaker segments)
- pipeline summary card
- identities & emotions list
- face boxes + labels over video playback (from `face_tracks.json` + `final_track_summary.json` content embedded in `ui.json`)

## Output Artifacts

Outputs are written to:

- `data/jobs/<job_id>/outputs/face_tracks.json`
- `data/jobs/<job_id>/outputs/emotions.json`
- `data/jobs/<job_id>/outputs/diarization.json`
- `data/jobs/<job_id>/outputs/transcript.json`
- `data/jobs/<job_id>/outputs/name_signals.json`
- `data/jobs/<job_id>/outputs/associations.json`
- `data/jobs/<job_id>/outputs/final_track_summary.json`
- `data/jobs/<job_id>/outputs/ui.json`
- `data/jobs/<job_id>/embeddings/face/<track_id>.npy`

## Identity Store Design

`identity_store/identities.json` schema:

```json
{
  "identities": [
    {
      "id": "0001",
      "name": "Anu",
      "embeddings": ["identity_store/embeddings/anu_job_track.npy"],
      "created_at": "...",
      "last_seen_at": "...",
      "sources": [{"job_id": "...", "track_id": "..."}]
    }
  ]
}
```

Enrollment policy:
- Auto-enroll only **high-confidence self-intros**.
- Never auto-enroll from mentions.

Matching policy:
- Cosine similarity against all stored embeddings.
- Status: `matched` / `maybe` / `unknown`.

## Common Failure Modes

- **False names from casual language**: guarded by title-case + self-intro rules (e.g., `I'm accountable...` should not match).
- **Off-screen speaker**: mapping may remain unresolved if no visible face track.
- **Ambiguous mentions**: mention signals are kept, but not used for auto-enrollment.

## Install & Test

```bash
pip install -r requirements.txt
pytest -q
```
