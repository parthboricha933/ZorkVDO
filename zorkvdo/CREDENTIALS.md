# ZorkVDO — Credentials Checklist

This file tracks every external credential the project needs. Update the
status column as you provide each one. **Never commit real values to git —
drop them into `services/backend/.env` instead.**

## Architecture

- **Auth**: Firebase Authentication (primary). Flutter signs in via Firebase
  Auth SDK → sends Firebase ID token to backend → backend verifies via
  `firebase-admin`. No bcrypt, no JWT_SECRET, no separate token issuance.
- **AI**: Gemini via `google-genai` SDK. Pluggable architecture supports
  adding new providers later, but only Gemini + Mock are wired in.
- **Storage**: user-scoped paths (`users/{uid}/uploads/...`,
  `users/{uid}/renders/...`, etc.) + global `templates/` and `cache/`.
- **DB**: Firestore (when service account is present), in-memory otherwise.
- **Video**: FFmpeg (primary, trim/scale/concat) + MoviePy (complex ops)
  + OpenCV + YOLOv11 + MediaPipe + EasyOCR + librosa.

## Status Legend

- ✅ **Provided** — credential is in `.env` and detected by the status probe
- ⏳ **Pending** — waiting for you to provide
- ⚪ **Optional** — only needed if you want that specific feature

---

## ✅ Already Provided

| Credential | Value Source | Used By | Status |
|---|---|---|---|
| `GEMINI_API_KEY` | You provided | GeminiProvider (chat + vision + embeddings) | ✅ In `.env` |
| `FIREBASE_API_KEY` | From `google-services.json` | Flutter client SDK | ✅ In `.env` |
| `FIREBASE_PROJECT_ID` | `zorkvdo` (from google-services.json) | Firebase Admin SDK + client | ✅ In `.env` |
| `FIREBASE_APP_ID` | `1:538884582505:android:...` | Flutter Android app | ✅ In `.env` |
| `FIREBASE_STORAGE_BUCKET` | `zorkvdo.firebasestorage.app` | Firebase Storage | ✅ In `.env` |
| `FIREBASE_MESSAGING_SENDER_ID` | `538884582505` | FCM push notifications | ✅ In `.env` |
| `google-services.json` | You uploaded | Flutter Android app config | ✅ Placed at `apps/flutter/android/app/google-services.json` |

---

## ⏳ Pending — Needed for Production

| # | Credential | Why | How to Provide | Status |
|---|---|---|---|---|
| 1 | `firebase-service-account.json` | Backend Firebase Admin SDK — needed to verify Firebase ID tokens + enable Firestore | Firebase Console → Project Settings → Service Accounts → Generate new private key → save at `config/firebase_config/firebase-service-account.json` | ⏳ |
| 2 | `FCM_SERVER_KEY` | Push notifications from backend → Flutter app | Firebase Console → Project Settings → Cloud Messaging → Server Key | ⏳ |

**That's it.** Two credentials. Everything else is either provided, optional, or auto-detected.

Once you provide #1:
- Backend can verify Firebase ID tokens → all authenticated endpoints work
- Set `DATABASE_BACKEND=firestore` in `.env` → data persists across restarts

Once you provide #2:
- Push notifications to mobile devices work

---

## ⚪ Optional — Wire In When You Want the Feature

| Feature | Credentials | How to Provide |
|---|---|---|
| Cloud storage (instead of local filesystem) | `STORAGE_PROVIDER=s3` + `S3_ACCESS_KEY` + `S3_SECRET_KEY` + `S3_BUCKET` | AWS IAM / Cloudflare R2 / MinIO / Wasabi |
| YOLOv11 object detection (currently disabled) | Install `ultralytics` package — `pip install ultralytics` | Auto-downloads `yolo11n.pt` on first use |
| MediaPipe pose detection (currently disabled) | Install `mediapipe` package — `pip install mediapipe` | Auto-bundles models |
| EasyOCR caption detection (currently disabled) | Install `easyocr` package — `pip install easyocr` | Auto-downloads models on first use |

---

## 🚫 Not Needed (per project spec)

The following were in my earlier assumptions but are NOT in your spec — I've removed them:

- ~~`JWT_SECRET`~~ — Firebase Auth handles all user auth
- ~~`JWT_REFRESH_SECRET`~~ — same
- ~~`ENCRYPTION_KEY`~~ — not in your spec
- ~~`OPENAI_API_KEY`~~ — only Gemini is the AI provider
- ~~`ANTHROPIC_API_KEY`~~ — same
- ~~`STRIPE_SECRET_KEY`~~ — not in your spec
- ~~`RESEND_API_KEY` / SMTP~~ — not in your spec
- ~~`POSTHOG_API_KEY` / `SENTRY_DSN`~~ — Firebase Analytics + Crashlytics handle these
- ~~`FIRESTORE_CONNECTION_STRING`~~ — Firebase Admin SDK uses service-account JSON
- ~~`STORAGE_CONNECTION_STRING`~~ — S3 backend uses discrete `S3_*` env vars
- ~~`ANALYTICS_KEY`~~ — Firebase Analytics is client-side via google-services.json
- ~~`CLOUD_STORAGE_KEY` / `CLOUD_STORAGE_SECRET` / `CLOUD_BUCKET_NAME`~~ — aliases for `S3_*`

---

## How to Provide the Pending Credentials

### Option A: Edit `.env` directly (recommended)

```bash
# 1. Download firebase-service-account.json
#    Firebase Console → Project Settings → Service Accounts → Generate new private key
#    Save to: /home/z/my-project/zorkvdo/config/firebase_config/firebase-service-account.json

# 2. Edit .env
nano /home/z/my-project/zorkvdo/services/backend/.env
# Set DATABASE_BACKEND=firestore
# Set FCM_SERVER_KEY=<your server key>

# 3. Restart the backend
pkill -f "uvicorn app.main:app"
cd /home/z/my-project/zorkvdo/services/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 4. Verify
curl http://localhost:8000/api/v1/status
# All Firebase integrations should now show 🟢 configured
```

### Option B: Paste credentials in chat

Just paste the FCM server key. For the service account JSON, paste its
contents and I'll write it to `config/firebase_config/firebase-service-account.json`
for you. I won't echo the values back.

---

## Architecture Guarantees

- ✅ **No hardcoded secrets** — every credential lives in `.env` or a config file
- ✅ **No secrets in client code** — Flutter reads Firebase config from `google-services.json` (gitignored)
- ✅ **Graceful degradation** — missing keys disable only the related feature
- ✅ **API status page** — `GET /api/v1/status` (unauthenticated) reports live status of all 17 integrations
- ✅ **Pluggable AI providers** — `AI_PROVIDER=mock|gemini` via env var (architecture supports adding more)
- ✅ **`.gitignore`** — `.env`, `google-services.json`, `firebase-service-account.json`, `storage_local/` all gitignored
- ✅ **Firebase Auth primary** — no JWT_SECRET, no bcrypt, no password hashing on backend
- ✅ **google-genai SDK** — Gemini uses the official unified SDK (not raw httpx)
- ✅ **MoviePy for complex ops** — text animations, PiP, transitions, audio mixing
- ✅ **YOLOv11** — default `YOLO_MODEL_PATH=yolo11n.pt` (configurable)
- ✅ **User-scoped storage paths** — `users/{uid}/uploads|renders|audio|thumbnails/` + global `templates/` + `cache/`
