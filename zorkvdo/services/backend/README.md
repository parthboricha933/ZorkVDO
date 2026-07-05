# ZorkVDO Backend

AI-powered viral video blueprint generator. Upload an existing viral video, the backend analyses it (scenes, beats, captions, motion, color, objects), and produces a reusable **Blueprint** JSON that the renderer can later use to assemble a brand-new video from your own clips.

## Quick start

### Local dev (no Docker)

```bash
cd services/backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

# Run the API
uvicorn app.main:app --reload --port 8000

# In another terminal — start the worker (optional, requires Redis)
celery -A app.workers.celery_app:celery_app worker --loglevel=INFO

# Or just run tests
pytest
```

The backend **boots without any external dependencies** — no Redis, no Firebase, no S3. It falls back to in-memory storage and the `mock` AI provider. Flip the relevant env vars to enable real backends.

### Docker Compose

```bash
cd infra/docker
docker compose up
# API on http://localhost:8000
# Flower on http://localhost:5555
# MinIO console on http://localhost:9001 (user: zorkvdo / pass: zorkvdo_secret)
```

## Project layout

```
services/backend/
├── app/
│   ├── api/                  # FastAPI routes + dependencies
│   │   ├── deps.py           # DI wiring
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── projects.py
│   │       ├── videos.py
│   │       ├── blueprints.py
│   │       ├── templates.py
│   │       ├── users.py
│   │       ├── jobs.py
│   │       ├── health.py
│   │       └── feedback.py
│   ├── core/                 # config, security, logging, exceptions
│   ├── db/                   # repository pattern (memory / firestore)
│   ├── models/               # Pydantic DTOs
│   ├── services/             # business logic (no FastAPI imports)
│   ├── storage/              # local / s3 / firebase
│   ├── workers/              # Celery tasks + renderer
│   └── main.py               # app factory + lifespan
├── tests/
│   ├── unit/                 # pure logic
│   └── integration/          # HTTP endpoint tests
└── pyproject.toml
```

## Packages

The monorepo ships two reusable Python packages:

- `packages/shared_schemas` — the **Blueprint JSON contract** (Pydantic models). Used by both the backend and (later) the Flutter app for type-safe Blueprint parsing.
- `packages/ai_engine` — provider-agnostic AI client + the full video analysis pipeline (OpenCV, librosa, easyocr, YOLO, MediaPipe).

Both are added to `sys.path` automatically by `app/_paths.py`.

## API overview

All endpoints live under `/api/v1`. Swagger docs at `/docs`.

| Group | Endpoints |
|---|---|
| **Auth** | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /auth/me`, `POST /auth/change-password` |
| **Projects** | `POST /projects`, `GET /projects`, `GET /projects/{id}`, `PATCH /projects/{id}`, `DELETE /projects/{id}` |
| **Videos** | `POST /videos/upload`, `GET /videos`, `GET /videos/{id}`, `GET /videos/{id}/download`, `DELETE /videos/{id}` |
| **Blueprints** | `GET /blueprints`, `GET /blueprints/{id}`, `DELETE /blueprints/{id}` |
| **Templates** | `GET /templates`, `GET /templates/{id}` |
| **Users** | `GET/PATCH /users/me/profile`, `GET/PATCH /users/me/settings`, `GET /users/plans`, `POST/DELETE /users/me/subscription`, `GET /users/me/notifications`, `GET /users/me/history`, `GET /users/me/analytics` |
| **Jobs** | `POST /jobs/analyze/{video_id}`, `GET /jobs`, `GET /jobs/{id}`, `POST /jobs/{id}/cancel` |
| **Misc** | `POST /feedback`, `GET /help`, `GET /health`, `GET /ready` |

## The Blueprint contract

The central artifact of the system. A Blueprint fully describes an editing style in a serialisable form:

```json
{
  "id": "bp_abc123",
  "name": "Viral TikTok Product Reveal",
  "meta": {
    "schema_version": "1.0.0",
    "generator": "zorkvdo-analyzer",
    "generated_at": "2025-07-05T10:00:00Z",
    "source_video_id": "vid_xyz",
    "source_duration_seconds": 14.5,
    "fps": 30.0,
    "width": 1080,
    "height": 1920
  },
  "pace": "fast",
  "overall_duration": 14.5,
  "scenes": [
    {
      "index": 0,
      "start": 0.0,
      "end": 0.8,
      "duration": 0.8,
      "shot_type": "wide",
      "camera_motion": "zoom_in",
      "zoom_factor": 1.2,
      "effects": [{"type": "zoom_bump", "intensity": 0.6, "duration": 0.2}],
      "transition_in": {"type": "cut", "duration": 0.1},
      "captions": [{"text": "WAIT FOR IT", "start": 0.0, "end": 0.6, ...}],
      "clip_suggestion": {
        "role": "hook",
        "preferred_shot": "wide",
        "duration_range": [0.6, 1.0],
        "motion": "zoom_in",
        "description": "Fill this 0.8s slot with hook footage."
      }
    }
    // ...more scenes
  ],
  "music": {"bpm": 128.0, "energy": 0.8, "beat_times": [...]},
  "color_grade": "teal_orange",
  "tags": ["pace:fast", "mood:energetic", "subject:person"]
}
```

Field names are part of the public API; new optional fields may be added but never renamed without bumping `meta.schema_version`.

## AI provider abstraction

The backend never hardcodes an AI provider. Set `AI_PROVIDER` to one of:

| Provider | When to use |
|---|---|
| `mock` (default) | Dev/tests — returns deterministic canned responses, no API key needed |
| `openai` | GPT-4o for chat + vision (set `OPENAI_API_KEY`) |
| `anthropic` | Claude 3.5 Sonnet (set `ANTHROPIC_API_KEY`) |
| `gemini` | Gemini 1.5 Pro (set `GEMINI_API_KEY`) |

Adding a new provider = implement the `AIProvider` protocol in `packages/ai_engine/zorkvdo_ai/providers/` and add a branch to `build_ai_client`.

## Video analysis pipeline

`VideoAnalyzer` orchestrates these independent passes in parallel:

| Pass | Library | Output |
|---|---|---|
| **Probe** | `ffprobe` | container metadata (duration, fps, codec, audio) |
| **Scene** | OpenCV (HSV histogram diff) | scene boundaries, shot durations |
| **Motion** | OpenCV (Lucas-Kanade optical flow) | per-frame pan/tilt/zoom/shake → dominant motion |
| **Beat** | librosa | BPM, beat times, onset times, energy |
| **Caption** | easyocr (lazy) | caption text + timing + position + color |
| **Color** | OpenCV k-means | dominant colors, brightness, saturation |
| **Object** | ultralytics YOLO (lazy) + OpenCV Haar + MediaPipe pose (lazy) | object counts, face count, pose presence |

All passes degrade gracefully: if `ultralytics` isn't installed, the object detector falls back to Haar cascades (which ship with `opencv-python-headless`). If `easyocr` isn't installed, captions are skipped but the rest of the analysis still runs.

## Configuration

All settings live in `app/core/config.py` and are loaded from environment variables (or `.env`). See `.env.example` for the full list.

**No secrets are hardcoded.** Every API key, password, and credentials path is a placeholder default that fails loud when used in production.

## Testing

```bash
pytest                    # full suite, 70% coverage gate
pytest tests/unit         # unit tests only
pytest tests/integration  # HTTP integration only
pytest --cov=app --cov=packages --cov-report=html
```

Tests use the in-memory repository + local filesystem storage + mock AI client. No Redis, no Firebase, no S3, no real video files required for the core suite.

## What's next (subsequent modules)

1. **Flutter app** (`apps/flutter`) — Riverpod 2 + Material 3, dark/light theme, onboarding, full screen flow.
2. **Cloud rendering** — swap the local FFmpeg renderer for a GPU-backed cloud service (Renderform, Banana, Modal, etc.).
3. **Collaborative editing** — websocket-based real-time project sync.
4. **Template marketplace** — community-uploaded blueprints with revenue share.
5. **AI voice / avatar / thumbnail / script generation** — additional AI provider methods on `AIClient`.

## License

Proprietary. © ZorkVDO.
