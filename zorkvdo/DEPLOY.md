# ZorkVDO Deployment Guide

This guide walks you through deploying ZorkVDO to production. You'll need:
- A GitHub account
- A Railway account (railway.app)
- A Firebase project (already set up — `zorkvdo`)

---

## Step 1: Push code to GitHub

The git repo is already initialized locally with a clean commit history.

### Create the repo on GitHub

1. Go to https://github.com/new
2. Repository name: `ZorkVDO`
3. Description: `AI-powered viral video blueprint engine`
4. Set to **Public** or **Private** (your choice)
5. **Don't** initialize with README/license/.gitignore (we already have them)
6. Click **Create repository**

### Push the code

```bash
cd /home/z/my-project

# Add your GitHub remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ZorkVDO.git

# Push
git push -u origin main
```

If you haven't authenticated git with GitHub, use a Personal Access Token:
1. Go to https://github.com/settings/tokens?type=beta
2. Generate a token with `Contents: Read and write` permission
3. When git prompts for password, paste the token

**Important**: Never paste the token in chat — use it directly in your terminal.

---

## Step 2: Deploy backend to Railway

### Create a Railway project

1. Go to https://railway.app/new
2. Click **Deploy from GitHub repo**
3. Select your `ZorkVDO` repo
4. Railway detects `railway.json` and uses the Dockerfile at `infra/docker/Dockerfile.backend`

### Configure environment variables

In the Railway dashboard → your project → **Variables** tab, add:

```env
APP_ENV=production
APP_PORT=8000
APP_LOG_LEVEL=INFO
APP_CORS_ORIGINS=https://zorkvdo-xxx.vercel.app,https://your-frontend-url.vercel.app

# AI
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_key_here
GEMINI_MODEL=gemini-1.5-pro

# Firebase
FIREBASE_API_KEY=AIzaSyBTIskiP89wQeEF9vmEzbgRgIH8MhE3v9c
FIREBASE_PROJECT_ID=zorkvdo
FIREBASE_APP_ID=1:538884582505:android:8346726273bcafc0fe86f8
FIREBASE_STORAGE_BUCKET=zorkvdo.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=538884582505
FIREBASE_CREDENTIALS_PATH=/app/config/firebase_config/firebase-service-account.json

# Database
DATABASE_BACKEND=firestore

# Storage
STORAGE_PROVIDER=firebase

# Video processing
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe
YOLO_MODEL_PATH=yolo11n.pt
ANALYSIS_SCENE_THRESHOLD=27.0
ANALYSIS_SAMPLE_FPS=2.0
ANALYSIS_MAX_VIDEO_SECONDS=600
ANALYSIS_OCR_LANGUAGES=en
ANALYSIS_ENABLE_FACE=true
ANALYSIS_ENABLE_POSE=true

# Demo mode (set to false in production once Firebase Auth is wired)
DEMO_MODE=false
```

### Add the Firebase service account

1. Go to Firebase Console → your project (`zorkvdo`) → Project Settings → Service Accounts
2. Click **Generate new private key** → download the JSON file
3. In Railway dashboard → your project → **Settings** → **Volumes** → add a volume mounted at `/app/config/firebase_config/`
4. Upload the service-account JSON as `firebase-service-account.json` to that volume

**Alternative**: Use Railway's **Raw environment variable** feature — base64-encode the JSON and store it as `FIREBASE_CREDENTIALS_BASE64`, then add a startup script that decodes it. Ask me if you need this approach.

### Deploy

Railway auto-deploys when you push to `main`. The first deploy takes ~5-8 minutes (building Docker image + installing YOLO/MediaPipe/EasyOCR).

Once deployed, Railway gives you a URL like `https://zorkvdo-backend-production.up.railway.app`. Test it:
```bash
curl https://your-railway-url/api/v1/health
# Should return: {"status":"ok","service":"zorkvdo-backend","version":"0.1.0"}
```

---

## Step 3: Update Vercel environment variables

1. Go to https://vercel.com/parthboricha933s-projects/zorkvdo/settings/environment-variables
2. Add a new variable:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-railway-url/api/v1` (replace with your actual Railway URL)
   - **Environment**: Production, Preview, Development
3. Redeploy the Vercel project (Deployments → click the latest → Redeploy)

---

## Step 4: Verify end-to-end

1. Visit your Vercel URL
2. Upload a viral video
3. Wait for analysis (should take 30-60s on Railway)
4. View the blueprint
5. Upload your clips
6. Click Render
7. Download the result

If anything fails, check:
- Railway logs (dashboard → your project → Deployments → click latest → Logs)
- Vercel logs (dashboard → your project → Functions → Logs)
- Backend status endpoint: `https://your-railway-url/api/v1/status`

---

## Optional: Add a Celery worker on Railway

The backend currently runs analysis inline (sync mode). For production with multiple users, add a separate worker:

1. In Railway dashboard → your project → **New Service** → **GitHub Repo** → same repo
2. Set the **start command** to:
   ```
   celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --concurrency=2
   ```
3. Add the same environment variables as the web service
4. Add a Redis service: Railway dashboard → **New Service** → **Database** → Redis
5. Update `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` to the Railway Redis connection string

---

## Troubleshooting

### Backend returns 401 on all endpoints
- `DEMO_MODE=false` is set but Firebase Auth isn't configured
- Verify `firebase-service-account.json` is at `FIREBASE_CREDENTIALS_PATH`
- Temporarily set `DEMO_MODE=true` to test without auth

### Video analysis fails
- Check that ffmpeg is installed: `ffmpeg -version` (should be in Docker image)
- Check that YOLO model downloads: first analysis may take longer (downloads `yolo11n.pt`)
- Check Railway logs for the specific error

### Upload fails with "unsupported content type"
- The backend infers content-type from filename extension
- Make sure the file has a `.mp4`, `.mov`, `.webm`, or `.mkv` extension

### Vercel site can't reach backend
- Verify `NEXT_PUBLIC_API_URL` is set on Vercel (Production environment)
- Verify the Railway URL is correct and public (not internal)
- Test with: `curl https://your-railway-url/api/v1/health`

---

## Security checklist

- [ ] `.env` is gitignored (verify: `git status` should not show `.env`)
- [ ] `google-services.json` is gitignored
- [ ] `firebase-service-account.json` is gitignored
- [ ] No API keys/tokens pasted in chat (use Railway/Vercel dashboards directly)
- [ ] Rotate any tokens that were accidentally exposed
- [ ] Set `DEMO_MODE=false` on Railway once Firebase Auth is verified working
