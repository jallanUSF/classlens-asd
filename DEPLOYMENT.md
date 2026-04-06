# ClassLens ASD — Deployment Guide

## Architecture

- **Frontend**: Next.js on Vercel — proxies `/api/*` to the backend
- **Backend**: FastAPI on Railway or Render — serves the API + runs Gemma agents

## Frontend (Vercel)

### Setup

1. Import the repo in Vercel, set **Root Directory** to `frontend`
2. Framework preset: **Next.js** (auto-detected)
3. Build command: `npm run build` (auto-detected)

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_URL` | Yes | Backend URL, e.g. `https://classlens-api.up.railway.app` |

Set `API_URL` in Vercel Project Settings > Environment Variables.

## Backend (Railway)

### Setup

1. Create new project, connect repo
2. Set **Root Directory** to `/` (project root)
3. Railway auto-detects the `Procfile`

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_AI_STUDIO_KEY` | Yes | Google AI Studio API key for Gemma 4 |
| `MODEL_PROVIDER` | No | `google` (default) or `openrouter` |
| `OPENROUTER_API_KEY` | If using OpenRouter | OpenRouter API key |
| `CORS_ORIGINS` | Yes | Comma-separated origins, e.g. `https://classlens.vercel.app` |
| `PYTHONPATH` | Yes | Set to `/app` (Railway) so imports from `core/`, `agents/`, `schemas/` resolve |
| `PORT` | Auto | Railway sets this automatically |

## Backend (Render) — Alternative

1. Create new **Web Service**, connect repo
2. Render reads `render.yaml` automatically (Blueprint)
3. Set secrets (`GOOGLE_AI_STUDIO_KEY`, `CORS_ORIGINS`) in the Render dashboard

## Verify Deployment

```bash
# Backend health check
curl https://your-backend-url.com/health
# Expected: {"status":"ok","version":"0.3.0"}

# Frontend — should proxy through to backend
curl https://your-frontend-url.vercel.app/api/students
```

## Preview Deployments

Vercel preview deploys (PRs) get `*.vercel.app` URLs. The backend CORS is configured
to accept any `*.vercel.app` origin via `allow_origin_regex`, so previews work
automatically without updating `CORS_ORIGINS`.
