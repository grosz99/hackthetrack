# 🚀 LOCAL DEVELOPMENT STARTUP GUIDE

## Quick Preview (Deployed Version)
The app is deployed on Vercel. Check your Vercel dashboard at https://vercel.com/dashboard for the live URL.

If you don't have the URL handy, run:
```bash
cd frontend && npx vercel --prod
```

---

## 🖥️ Running Locally (Full Stack)

### Prerequisites
- Python 3.12+ installed
- Node.js 18+ installed
- Terminal access

### Step 1: Start Backend Server

Open **Terminal 1**:

```bash
# Navigate to project root
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Navigate to backend
cd backend

# Activate virtual environment (if not already active)
source venv/bin/activate

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the backend server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

✅ **Backend is running at http://localhost:8000**

Test it:
```bash
curl http://localhost:8000/api/health
```

---

### Step 2: Start Frontend Dev Server

Open **Terminal 2** (new tab):

```bash
# Navigate to project root
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Navigate to frontend
cd frontend

# Install dependencies (if not already done)
npm install

# Start the dev server
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ **Frontend is running at http://localhost:5173**

---

### Step 3: Open in Browser

Open your browser and go to:
```
http://localhost:5173
```

You should see the HackTheTrack landing page!

---

## 🐛 Troubleshooting

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Error**: `Address already in use`

**Solution**: Another process is using port 8000. Kill it:
```bash
lsof -ti:8000 | xargs kill -9
```

---

### Frontend won't start

**Error**: `Cannot find module 'vite'`

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error**: `EADDRINUSE: address already in use :::5173`

**Solution**: Another process is using port 5173. Kill it:
```bash
lsof -ti:5173 | xargs kill -9
```

---

### API calls failing (Network Error)

**Check 1**: Is backend running?
```bash
curl http://localhost:8000/api/health
```

**Check 2**: Is frontend pointing to correct backend?
```bash
cat frontend/.env
# Should show: VITE_API_URL=http://localhost:8000
```

**Fix**: If .env doesn't exist:
```bash
cd frontend
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev  # Restart
```

---

### Database issues

**Error**: `no such table: drivers`

**Solution**: Database file might be missing. Check:
```bash
ls -la backend/circuit-fit.db
```

If missing, the backend should create it automatically on first run.

---

## 📦 Quick Start Script

Want to start everything with one command? Create this script:

```bash
#!/bin/bash
# File: start-dev.sh

# Start backend in background
cd backend
source venv/bin/activate
python main.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Starting backend..."
sleep 3

# Start frontend
cd ../frontend
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
```

Make it executable:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

---

## 🌐 Viewing Deployed Version

### Option 1: Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Find your project "hackthetrack" or similar
3. Click on the production deployment
4. Copy the URL (usually something like `https://hackthetrack-xxx.vercel.app`)

### Option 2: Deploy from CLI
```bash
cd frontend
npx vercel --prod
```

This will give you the production URL.

---

## ✅ Verification Checklist

After starting both servers, verify everything works:

- [ ] Backend health check: http://localhost:8000/api/health
- [ ] Backend drivers endpoint: http://localhost:8000/api/drivers
- [ ] Frontend loads: http://localhost:5173
- [ ] Can navigate to different pages
- [ ] Driver data loads on Overview page
- [ ] No console errors (F12 → Console tab)

---

## 🎯 Next Steps After Local Setup

Once you confirm everything works locally:

1. **Test the new changes**:
   - Go to Improve page (`/driver/13/improve`)
   - Verify layout is equal-sized (left and right sections)
   - Verify no emojis appear
   - Test similar driver matching (should only show better drivers)

2. **Test desktop responsiveness**:
   - Open Overview page
   - Zoom browser to 150%
   - Verify content doesn't appear too zoomed in

3. **Test navigation flow**:
   - Race Log → Click "View Skills Breakdown" button
   - Skills → Click on skill tiles
   - Verify detail section appears below

---

## 💡 Development Tips

### Hot Reload
- **Frontend**: Changes auto-reload (save file → browser refreshes)
- **Backend**: Changes auto-reload (save file → server restarts)

### Viewing Backend API Docs
FastAPI auto-generates docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Viewing Database
Use a SQLite viewer like DB Browser for SQLite:
```bash
open backend/circuit-fit.db
```

---

## 🔥 Common Development Workflow

1. Make code changes in your editor
2. Save files (auto-reload happens)
3. Check browser for frontend changes
4. Check Terminal 1 for backend logs
5. Use browser DevTools (F12) for debugging

---

## 📞 Still Having Issues?

If localhost still doesn't work after following this guide:

1. **Check what's using the ports**:
   ```bash
   lsof -i :8000  # Backend port
   lsof -i :5173  # Frontend port
   ```

2. **Check environment variables**:
   ```bash
   cd frontend && cat .env
   cd backend && cat .env
   ```

3. **Check Python version**:
   ```bash
   python --version  # Should be 3.12+
   ```

4. **Check Node version**:
   ```bash
   node --version  # Should be 18+
   ```

---

**Happy Coding! 🎉**
