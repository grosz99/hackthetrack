# Vercel Frontend-Only Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   USER BROWSER                           │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────┐
│              VERCEL CDN (Frontend)                       │
│  - React SPA (Static Files)                             │
│  - Optimized Asset Delivery                             │
│  - Global Edge Network                                  │
└───────────────────┬─────────────────────────────────────┘
                    │
                    │ API Calls (VITE_API_URL)
                    ▼
┌─────────────────────────────────────────────────────────┐
│           RAILWAY (Backend API)                          │
│  - FastAPI Python Backend                               │
│  - All /api/* endpoints                                 │
│  - Database connections                                 │
│  - Heavy computation                                    │
└─────────────────────────────────────────────────────────┘
```

## Critical Findings

### 1. Frontend Configuration Analysis

**GOOD NEWS**: Your frontend is already well-prepared for external API deployment:

- ✅ Centralized API service layer (`/Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend/src/services/api.js`)
- ✅ Environment-aware API URL configuration
- ✅ All API calls go through the service layer
- ✅ No hardcoded localhost URLs in components
- ✅ Proper VITE_API_URL usage

**API Service Configuration**:
```javascript
const getApiBaseUrl = () => {
  if (import.meta.env.PROD) {
    return '';  // ⚠️ NEEDS UPDATE
  }
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};
```

**ISSUE**: Production mode returns empty string, expecting `/api` routes to be local. This needs to change.

### 2. Build Analysis

**Build Output**:
- ✅ Build completes successfully
- ⚠️ Bundle size: 856.18 kB (gzipped: 239.85 kB)
- ⚠️ Warning: Chunks larger than 500 kB after minification
- ✅ Output directory: `frontend/dist/`
- ✅ Assets properly organized

**Bundle Size Concerns**:
Large bundle likely due to:
- Plotly.js (heavy charting library)
- React Router
- Recharts
- React Markdown

### 3. Environment Variable Usage

**Current Pages Using API**:
- DriverContext.jsx - Loads driver data
- Improve.jsx - AI coaching telemetry
- Overview.jsx - Driver statistics
- Skills.jsx - Performance factors
- RaceLog.jsx - Race results

All properly use the `api` service from `/services/api.js`.

## Deployment Steps

### Phase 1: Update Frontend API Configuration

**File**: `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend/src/services/api.js`

**Change Required**:
```javascript
// BEFORE (current)
const getApiBaseUrl = () => {
  if (import.meta.env.PROD) {
    return '';  // Empty string - routes already include /api prefix
  }
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};

// AFTER (for Railway backend)
const getApiBaseUrl = () => {
  // Always use environment variable in production
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};
```

### Phase 2: Vercel Project Configuration

**1. Create New Vercel Project**
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project root
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
vercel
```

**2. Configure Build Settings in Vercel Dashboard**

Navigate to: Project Settings → General

```
Framework Preset: Vite
Root Directory: ./
Build Command: cd frontend && npm ci && npm run build
Output Directory: frontend/dist
Install Command: cd frontend && npm ci
```

**3. Set Environment Variables**

Navigate to: Project Settings → Environment Variables

Add the following for **Production**:

```
Variable Name: VITE_API_URL
Value: https://your-railway-backend.railway.app
Environment: Production
```

**IMPORTANT**: The Railway backend URL must NOT have a trailing slash.

### Phase 3: Railway Backend Setup

**1. Deploy Backend to Railway**

From backend directory:
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend

# Create railway.toml if not exists
```

**2. Configure CORS for Railway**

Update backend to allow Vercel domain:

```python
# backend/main.py or wherever CORS is configured
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",  # Local dev
    "https://your-vercel-app.vercel.app",  # Vercel production
    "https://*.vercel.app",  # Vercel preview deployments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**3. Get Railway URL**

After deployment, Railway provides a URL like:
```
https://your-backend-name.railway.app
```

Copy this URL and set it in Vercel environment variables.

### Phase 4: Build Optimization (Optional but Recommended)

**Update**: `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend/vite.config.js`

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react({
    jsxRuntime: 'automatic'
  })],
  base: '/',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,  // Disable in production for smaller builds
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom', 'react-router-dom'],
          'charts': ['plotly.js', 'react-plotly.js', 'recharts'],
          'markdown': ['react-markdown']
        }
      }
    },
    chunkSizeWarningLimit: 1000
  }
})
```

## Testing Checklist

### Local Testing (Before Deploy)

```bash
# 1. Update API service to use VITE_API_URL
cd frontend/src/services

# 2. Build frontend
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend
npm run build

# 3. Preview production build locally
npm run preview

# 4. Test with Railway backend URL
VITE_API_URL=https://your-railway-backend.railway.app npm run preview
```

**Manual Test Cases**:
- [ ] Homepage loads
- [ ] Driver selector dropdown populates
- [ ] Overview page shows driver stats
- [ ] Race Log page displays race results
- [ ] Skills page shows performance factors
- [ ] Improve page loads AI coaching
- [ ] Navigation between pages works
- [ ] SPA routing (refresh on any page) works
- [ ] No console errors related to API calls

### Post-Deployment Verification

**1. Deployment Success**
- [ ] Vercel build completes without errors
- [ ] Build logs show successful compilation
- [ ] No warnings about missing environment variables

**2. Static File Serving**
- [ ] Navigate to Vercel URL
- [ ] Homepage loads correctly
- [ ] Assets (CSS, JS) load from CDN
- [ ] Images and track maps display
- [ ] No 404 errors in Network tab

**3. SPA Routing**
- [ ] Direct navigation to `/overview` works
- [ ] Direct navigation to `/skills` works
- [ ] Direct navigation to `/improve` works
- [ ] Browser refresh maintains page (no 404)

**4. API Integration**
- [ ] Open browser DevTools → Network tab
- [ ] Check API calls go to Railway backend URL
- [ ] Verify API responses return data
- [ ] Check for CORS errors (should be none)
- [ ] Test all major features that depend on API

**5. Performance**
- [ ] Lighthouse score > 90 for Performance
- [ ] First Contentful Paint < 2s
- [ ] Time to Interactive < 3s
- [ ] Check CDN headers on assets

## Deployment Commands

**Production Deployment**:
```bash
# From project root
vercel --prod
```

**Preview Deployment** (for testing):
```bash
vercel
```

**Check Deployment Status**:
```bash
vercel ls
```

**View Logs**:
```bash
vercel logs [deployment-url]
```

## Environment Variables Summary

### Vercel (Frontend)

| Variable | Value | Environment | Purpose |
|----------|-------|-------------|---------|
| VITE_API_URL | https://your-railway-backend.railway.app | Production | Backend API endpoint |

**Note**: Vite only exposes variables prefixed with `VITE_` to the client.

### Railway (Backend)

Configure in Railway dashboard:

| Variable | Example Value | Purpose |
|----------|---------------|---------|
| DATABASE_URL | postgresql://... | Database connection |
| ANTHROPIC_API_KEY | sk-ant-... | Claude API |
| CORS_ORIGINS | https://your-app.vercel.app | Frontend domain |

## Troubleshooting

### Issue: API calls returning 404

**Cause**: VITE_API_URL not set or incorrect

**Solution**:
1. Check Vercel environment variables
2. Verify Railway backend URL is correct
3. Rebuild frontend after changing env vars

### Issue: CORS errors

**Cause**: Backend not configured to allow Vercel domain

**Solution**:
```python
# Update backend CORS configuration
origins = [
    "https://your-vercel-app.vercel.app",
    "https://*.vercel.app"
]
```

### Issue: SPA routing returns 404 on refresh

**Cause**: Rewrites not configured properly

**Solution**: Verify `vercel.json` has:
```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Issue: Slow load times

**Cause**: Large bundle size

**Solution**:
1. Enable code splitting in vite.config.js
2. Use dynamic imports for heavy components
3. Consider lazy loading chart libraries

### Issue: Environment variables not applied

**Cause**: Need to rebuild after env var changes

**Solution**:
1. Trigger new deployment in Vercel
2. Or redeploy: `vercel --prod`

## File Modifications Summary

### Modified Files

1. `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/vercel.json`
   - Removed backend API route rewrites
   - Added SPA fallback rewrite
   - Added security headers
   - Added cache headers for assets

2. `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend/.env.production`
   - Updated VITE_API_URL to point to Railway

3. `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend/src/services/api.js`
   - **NEEDS UPDATE**: Change production API URL logic

### Required Backend Changes

1. Update CORS configuration to allow Vercel domain
2. Ensure all `/api/*` routes are working
3. Configure Railway environment variables

## Next Steps

1. ✅ Update `frontend/src/services/api.js` (see Phase 1)
2. ✅ Deploy backend to Railway first
3. ✅ Get Railway backend URL
4. ✅ Set VITE_API_URL in Vercel
5. ✅ Deploy frontend to Vercel
6. ✅ Test all functionality
7. ✅ Monitor logs for errors

## Performance Recommendations

### Current Bundle Analysis

```
Bundle Size: 856.18 kB (minified)
Gzipped: 239.85 kB

Largest Dependencies:
- plotly.js: ~3.1 MB (likely largest contributor)
- react-plotly.js: Wrapper around plotly
- recharts: Additional charting library
- react-router-dom: Routing
- react-markdown: Markdown rendering
```

### Optimization Strategies

**1. Code Splitting (High Impact)**
```javascript
// Lazy load heavy pages
const Improve = lazy(() => import('./pages/Improve/Improve'));
const Skills = lazy(() => import('./pages/Skills/Skills'));
```

**2. Chart Library Optimization (High Impact)**
- Consider replacing Plotly with lighter alternatives for some charts
- Use dynamic imports for chart components
- Load Plotly only on pages that need it

**3. Bundle Analysis**
```bash
npm run build -- --mode analyze
# Install rollup-plugin-visualizer if needed
```

## Success Metrics

**Deployment Success**:
- ✅ Vercel build completes in < 2 minutes
- ✅ No build errors or warnings
- ✅ All assets uploaded to CDN

**Runtime Success**:
- ✅ All pages load without errors
- ✅ API calls succeed with Railway backend
- ✅ Navigation works smoothly
- ✅ No CORS errors
- ✅ Lighthouse score > 85

**User Experience**:
- ✅ Page load < 3 seconds
- ✅ Smooth interactions
- ✅ Data loads correctly
- ✅ Charts render properly

## Cost Considerations

**Vercel Free Tier Limits**:
- 100 GB bandwidth/month
- 6,000 build minutes/month
- Unlimited deployments

**Railway Starter Plan**:
- $5/month credit
- Pay for what you use
- Estimated ~$10-20/month for backend

**Total Estimated Cost**: $10-20/month

## Rollback Plan

If deployment fails:

1. **Keep existing setup running** during deployment
2. **Test in Vercel preview** before promoting to production
3. **Use Vercel's instant rollback**:
   ```bash
   vercel rollback [deployment-url]
   ```
4. **Revert API URL** in environment variables if needed

## Support Resources

- Vercel Documentation: https://vercel.com/docs
- Railway Documentation: https://docs.railway.app
- Vite Documentation: https://vitejs.dev
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
