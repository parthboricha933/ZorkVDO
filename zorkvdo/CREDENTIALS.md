# ZorkVDO — Credentials Checklist

This file tracks every external credential the project needs. Update the
status column as you provide each one. **Never commit real values to git —
drop them into `services/backend/.env` instead.**

## Status Legend

- ✅ **Provided** — credential is in `.env` and detected by the status probe
- ⏳ **Pending** — waiting for you to provide
- ⚪ **Optional** — only needed if you want that specific feature
- 🚫 **Not needed** — architecture doesn't require it

---

## ✅ Already Provided

| Credential | Value Source | Used By | Status |
|---|---|---|---|
| `GEMINI_API_KEY` | You provided | GeminiProvider — AI chat + vision | ✅ In `.env` |
| `FIREBASE_API_KEY` | From `google-services.json` | Flutter client SDK | ✅ In `.env` |
| `FIREBASE_PROJECT_ID` | `zorkvdo` (from google-services.json) | Firebase Admin SDK + client | ✅ In `.env` |
| `FIREBASE_APP_ID` | `1:538884582505:android:...` | Flutter Android app | ✅ In `.env` |
| `FIREBASE_STORAGE_BUCKET` | `zorkvdo.firebasestorage.app` | Firebase Storage | ✅ In `.env` |
| `FIREBASE_MESSAGING_SENDER_ID` | `538884582505` | FCM push notifications | ✅ In `.env` |
| `google-services.json` | You uploaded | Flutter Android app config | ✅ Placed at `apps/flutter/android/app/google-services.json` |

---

## ⏳ Pending — Needed for Production

| Credential | Why | Where to Get It | Status |
|---|---|---|---|
| `JWT_SECRET` | Signs all access tokens (currently a dev placeholder) | Run: `openssl rand -hex 32` | ⏳ |
| `JWT_REFRESH_SECRET` | Signs refresh tokens (currently a dev placeholder) | Run: `openssl rand -hex 32` (separate from above) | ⏳ |
| `ENCRYPTION_KEY` | Field-level AES encryption for sensitive data at rest | Run: `openssl rand -hex 16` | ⏳ |
| `firebase-service-account.json` | Backend Firebase Admin SDK (Firestore + Auth verification) | Firebase Console → Project Settings → Service Accounts → Generate new private key | ⏳ Drop at `config/firebase_config/firebase-service-account.json` |
| `FCM_SERVER_KEY` | Push notifications from backend → Flutter app | Firebase Console → Project Settings → Cloud Messaging → Server Key | ⏳ |

---

## ⚪ Optional — Wire In When You Want the Feature

| Credential | Why | Where to Get It | Status |
|---|---|---|---|
| `STRIPE_SECRET_KEY` | Accept real subscription payments | dashboard.stripe.com → Developers → API keys | ⚪ |
| `STRIPE_WEBHOOK_SECRET` | Verify Stripe webhook signatures | Stripe dashboard → Webhooks → your endpoint → Signing secret | ⚪ |
| `STRIPE_PRICE_CREATOR_MONTHLY` | Stripe Price ID for Creator plan monthly | Create product in Stripe → copy price ID (`price_...`) | ⚪ |
| `STRIPE_PRICE_CREATOR_YEARLY` | Stripe Price ID for Creator plan yearly | Same as above | ⚪ |
| `STRIPE_PRICE_PRO_MONTHLY` | Stripe Price ID for Pro plan monthly | Same as above | ⚪ |
| `STRIPE_PRICE_PRO_YEARLY` | Stripe Price ID for Pro plan yearly | Same as above | ⚪ |
| `RESEND_API_KEY` | Transactional email (welcome, password reset, render-complete) | resend.com → API Keys | ⚪ |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USER` / `SMTP_PASSWORD` | Alternative to Resend for email | Your SMTP provider | ⚪ |
| `POSTHOG_API_KEY` | Product analytics (funnels, retention, feature usage) | app.posthog.com → Project Settings → API Key | ⚪ |
| `SENTRY_DSN` | Production error tracking | sentry.io → Project Settings → Client Keys | ⚪ |
| `S3_ACCESS_KEY` + `S3_SECRET_KEY` | Cloud storage (when you outgrow local filesystem) | AWS IAM, Cloudflare R2, MinIO, Wasabi, etc. | ⚪ |
| `S3_BUCKET` | Bucket name for cloud storage | Create bucket in your S3-compatible provider | ⚪ |
| `OPENAI_API_KEY` | Optional alternative AI provider | platform.openai.com → API keys | ⚪ |
| `ANTHROPIC_API_KEY` | Optional alternative AI provider | console.anthropic.com → API Keys | ⚪ |

---

## 🚫 Not Needed

The following are NOT required because the architecture handles them differently:

| Item | Why Not Needed |
|---|---|
| `FFMPEG_PATH` / `FFPROBE_PATH` | Already installed at `/usr/bin/ffmpeg` — auto-detected |
| `YOLO_MODEL_PATH` | Auto-downloads `yolov8n.pt` on first use via ultralytics |
| `MEDIAPIPE_MODEL_PATH` | MediaPipe bundles its models |
| `OCR_MODEL_PATH` | EasyOCR auto-downloads models |
| `OPENCV_PATH` | Haar cascade XML ships with `opencv-python-headless` |
| `FIRESTORE_CONNECTION_STRING` | Firebase Admin SDK uses the service-account JSON instead |
| `STORAGE_CONNECTION_STRING` | S3 backend uses discrete `S3_*` env vars |
| `ANALYTICS_KEY` | Use provider-specific keys (`POSTHOG_API_KEY`, etc.) instead |
| `CLOUD_STORAGE_KEY` / `CLOUD_STORAGE_SECRET` / `CLOUD_BUCKET_NAME` | Aliases for `S3_*` — not separately required |

---

## How to Provide the Pending Credentials

### Option A: Edit `.env` directly (recommended)

```bash
# 1. Generate strong secrets
openssl rand -hex 32  # → copy to JWT_SECRET in .env
openssl rand -hex 32  # → copy to JWT_REFRESH_SECRET in .env
openssl rand -hex 16  # → copy to ENCRYPTION_KEY in .env

# 2. Edit the .env file
nano /home/z/my-project/zorkvdo/services/backend/.env
# Fill in the ⏳ Pending values

# 3. Drop the Firebase service account JSON in place
# Download from Firebase Console → Project Settings → Service Accounts → Generate new private key
# Save to: /home/z/my-project/zorkvdo/config/firebase_config/firebase-service-account.json

# 4. Flip DATABASE_BACKEND to firestore
# In .env, change: DATABASE_BACKEND=firestore

# 5. Restart the backend
pkill -f "uvicorn app.main:app"
cd /home/z/my-project/zorkvdo/services/backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 6. Verify by hitting the status endpoint
curl -H "Authorization: Bearer <your-token>" http://localhost:8000/api/v1/status
```

### Option B: Paste credentials in chat

Just paste each credential value and I'll wire it into `.env` for you. I'll never echo the full value back.

---

## Architecture Guarantees

- ✅ **No hardcoded secrets** — every credential lives in `.env` or a config file
- ✅ **Graceful degradation** — missing keys disable only the related feature
- ✅ **API status page** — `GET /api/v1/status` reports live status of every integration
- ✅ **Pluggable AI providers** — swap `AI_PROVIDER=gemini|openai|anthropic|mock` via env var
- ✅ **`.gitignore`** — `.env`, `google-services.json`, `firebase-service-account.json` all gitignored
- ✅ **No secrets in client code** — Flutter app reads Firebase config from `google-services.json` (which is gitignored), backend reads everything else from env vars
