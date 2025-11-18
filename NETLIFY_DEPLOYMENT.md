# Netlify Deployment Guide for Gibbs AI

This project is configured for **frontend-only deployment** on Netlify with:
- **Frontend**: React + Vite on Netlify (publicly accessible, no authentication)
- **Backend**: FastAPI on Heroku (existing deployment with all data)
- **Architecture**: Frontend calls Heroku API via CORS

## Prerequisites

1. Netlify account (free tier works perfectly)
2. GitHub repository connected to Netlify

## One-Click Deployment

### Option 1: Deploy via Netlify Dashboard (Recommended)

1. **Go to Netlify**: https://app.netlify.com
2. **Click "Add new site"** → "Import an existing project"
3. **Connect GitHub** and select this repository
4. **Configure build settings** (should auto-detect from `netlify.toml`):
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `frontend/dist`
   - Functions directory: `netlify/functions`

5. **No environment variables needed for frontend!**

   The frontend only needs `VITE_API_URL` which is already set in `netlify.toml` to point to Heroku.

6. **Click "Deploy site"**

7. **Set custom domain** (optional):
   - Go to Site settings → Domain management
   - Recommended: `gibbs-ai.netlify.app` or your custom domain

### Option 2: Deploy via Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Link to existing site or create new one
netlify link

# Deploy to production
netlify deploy --prod
```

## Architecture

```
Frontend (Netlify - Public)
https://gibbs-ai.netlify.app/
├── /                    → React SPA
├── /driver/7            → Driver pages
├── /rankings            → Rankings page
└── ...                  → All frontend routes
                  │
                  │ CORS requests
                  ↓
Backend (Heroku - Existing)
https://hackthetrack-api-ae28ad6f804d.herokuapp.com
├── /api/drivers         → Driver endpoints
├── /api/factors         → 4-Factor endpoints
├── /api/coaching        → AI coaching endpoints
└── ...                  → All API routes
```

## Key Files

- **`netlify.toml`**: Main configuration (build settings, redirects, environment)
- **`netlify/functions/api.py`**: FastAPI serverless wrapper using Mangum
- **`backend/requirements.txt`**: Python dependencies for backend
- **`frontend/package.json`**: Node dependencies for frontend

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key for coaching features | `sk-ant-api03-...` |

**Data Source**: All race telemetry is served from CSV/JSON files in `backend/data/`. No database connection required.

## Deployment Workflow

1. **Push to GitHub** → Automatic deployment triggered
2. **Netlify builds frontend** (`npm run build` in `frontend/`)
3. **Netlify packages backend** (installs `requirements.txt` dependencies)
4. **Deploy completes** → Site live at `https://your-site.netlify.app`

## Benefits Over Vercel + Heroku

✅ **Public by default** - No authentication required
✅ **Unified deployment** - Frontend + Backend in one place
✅ **Zero cold starts** - Netlify Edge Functions are fast
✅ **Automatic HTTPS** - SSL certificates included
✅ **Free tier sufficient** - No upgrade needed
✅ **Simple environment variables** - Set once in dashboard
✅ **Automatic previews** - Every PR gets a preview URL

## Troubleshooting

### Backend functions not working?
- Check Netlify Functions logs: Site → Functions → Logs
- Verify environment variables are set
- Ensure `mangum` is in `requirements.txt`

### Frontend can't reach API?
- API routes must start with `/api/`
- Check CORS settings in `backend/main.py`
- Verify redirects in `netlify.toml`

### Build failures?
- Check build logs in Netlify dashboard
- Verify `requirements.txt` has all dependencies
- Ensure Node version is 18+ (set in `netlify.toml`)

## Local Development

Frontend and backend still run separately for development:

```bash
# Terminal 1: Frontend
cd frontend
npm run dev
# → http://localhost:5173

# Terminal 2: Backend
cd backend
python main.py
# → http://localhost:8000
```

Set `VITE_API_URL=http://localhost:8000` in `frontend/.env.local` for local development.

## Support

For deployment issues, check:
- Netlify Status: https://www.netlifystatus.com/
- Netlify Community: https://answers.netlify.com/
- FastAPI + Netlify guide: https://www.mangum.io/
