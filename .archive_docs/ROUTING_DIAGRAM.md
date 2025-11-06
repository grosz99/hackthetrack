# Vercel Routing Architecture Diagram

## Request Flow Overview

```
                           Incoming Request
                                  |
                                  v
                    ┌─────────────────────────────┐
                    │    Vercel Edge Network      │
                    │  (CDN + Load Balancing)     │
                    └─────────────────────────────┘
                                  |
                                  v
                    ┌─────────────────────────────┐
                    │     vercel.json Routes      │
                    │   (Process in order)        │
                    └─────────────────────────────┘
                                  |
                ┌─────────────────┴─────────────────┐
                |                                   |
                v                                   v
    ┌──────────────────────┐          ┌──────────────────────┐
    │  API Request?        │          │  Static Asset?       │
    │  /api/*              │          │  /assets/*           │
    └──────────────────────┘          │  /track_maps/*       │
                |                     │  *.js, *.css, etc    │
                v                     └──────────────────────┘
    ┌──────────────────────┐                    |
    │  Backend Serverless  │                    v
    │  Function            │          ┌──────────────────────┐
    │  /backend/api/       │          │  Serve Static File   │
    │  index.py            │          │  from frontend/dist/ │
    └──────────────────────┘          └──────────────────────┘
                |
                v
    ┌──────────────────────┐
    │  Mangum Adapter      │
    │  (Lambda/ASGI)       │
    └──────────────────────┘
                |
                v
    ┌──────────────────────┐
    │  FastAPI App         │
    │  (main.py)           │
    └──────────────────────┘
                |
                v
    ┌──────────────────────┐
    │  API Routes          │
    │  (app/api/routes.py) │
    └──────────────────────┘
                |
                v
    ┌──────────────────────┐
    │  Services            │
    │  (data_loader,       │
    │   ai_strategy, etc)  │
    └──────────────────────┘
                |
                v
    ┌──────────────────────┐
    │  SQLite Database     │
    │  (circuit-fit.db)    │
    └──────────────────────┘
```

## Route Processing Order (Critical!)

```
Request: https://your-app.vercel.app/[path]
         │
         v
┌────────────────────────────────────────────────────────────────┐
│ 1. Check: /api/(.*)                                            │
│    Match: /api/health, /api/drivers, /api/*, etc              │
│    Action: Execute /backend/api/index.py                       │
│    Result: FastAPI handles request → JSON response             │
└────────────────────────────────────────────────────────────────┘
         │ No match
         v
┌────────────────────────────────────────────────────────────────┐
│ 2. Check: /assets/(.*)                                         │
│    Match: /assets/index-DhxXsaDh.js, /assets/index.css        │
│    Action: Serve /frontend/dist/assets/$1                      │
│    Result: Static JS/CSS file returned                         │
└────────────────────────────────────────────────────────────────┘
         │ No match
         v
┌────────────────────────────────────────────────────────────────┐
│ 3. Check: /track_maps/(.*)                                     │
│    Match: /track_maps/monaco.svg, /track_maps/*.png           │
│    Action: Serve /frontend/dist/track_maps/$1                  │
│    Result: Track map image returned                            │
└────────────────────────────────────────────────────────────────┘
         │ No match
         v
┌────────────────────────────────────────────────────────────────┐
│ 4. Check: /vite.svg                                            │
│    Match: /vite.svg                                            │
│    Action: Serve /frontend/dist/vite.svg                       │
│    Result: Vite logo returned                                  │
└────────────────────────────────────────────────────────────────┘
         │ No match
         v
┌────────────────────────────────────────────────────────────────┐
│ 5. Check: /(.*)\\.(js|css|png|jpg|jpeg|gif|svg|ico|json...)   │
│    Match: Any file with static extension                       │
│    Action: Serve /frontend/dist/$1                             │
│    Result: Static file returned                                │
└────────────────────────────────────────────────────────────────┘
         │ No match
         v
┌────────────────────────────────────────────────────────────────┐
│ 6. Check: /(.*)    ← CATCH-ALL (MUST BE LAST!)                │
│    Match: /, /scout, /scout/driver/1/overview, etc            │
│    Action: Serve /frontend/dist/index.html                     │
│    Result: React app loads, React Router handles route         │
└────────────────────────────────────────────────────────────────┘
```

## Example Request Flows

### Example 1: Homepage

```
User navigates to: https://your-app.vercel.app/

Route 1: /api/(.*)                    → No match
Route 2: /assets/(.*)                 → No match  
Route 3: /track_maps/(.*)             → No match
Route 4: /vite.svg                    → No match
Route 5: /(.*)\\.(ext)                → No match
Route 6: /(.*)                        → ✓ MATCH!

Action: Serve /frontend/dist/index.html

Result:
  1. Browser receives index.html
  2. HTML references /assets/index-DhxXsaDh.js
  3. Browser requests /assets/index-DhxXsaDh.js
  4. Route 2 matches → JS file served
  5. React app boots
  6. React Router renders "/" route (Scout Landing)
```

### Example 2: React Router Navigation

```
User navigates to: https://your-app.vercel.app/scout/driver/1/overview

Route 1: /api/(.*)                    → No match
Route 2: /assets/(.*)                 → No match
Route 3: /track_maps/(.*)             → No match
Route 4: /vite.svg                    → No match
Route 5: /(.*)\\.(ext)                → No match
Route 6: /(.*)                        → ✓ MATCH!

Action: Serve /frontend/dist/index.html (same as homepage!)

Result:
  1. Browser receives index.html
  2. React app boots with same JS bundle
  3. React Router sees /scout/driver/1/overview in URL
  4. React Router renders correct component (Overview page)
  5. User sees driver overview page

This is why SPA routing works! All non-API, non-asset routes 
serve the same HTML, React handles the rest.
```

### Example 3: API Request

```
User clicks button that calls: https://your-app.vercel.app/api/drivers

Route 1: /api/(.*)                    → ✓ MATCH!

Action: Execute /backend/api/index.py

Result:
  1. Vercel invokes Python serverless function
  2. index.py imports FastAPI app from main.py
  3. Mangum adapter converts Lambda event to ASGI
  4. FastAPI routes request to /api/drivers endpoint
  5. app/api/routes.py handles request
  6. Services/data_loader.py queries database
  7. JSON response returned to browser
```

### Example 4: Static Asset (CSS)

```
Browser requests: https://your-app.vercel.app/assets/index-Bnz4PAGb.css

Route 1: /api/(.*)                    → No match
Route 2: /assets/(.*)                 → ✓ MATCH!

Action: Serve /frontend/dist/assets/index-Bnz4PAGb.css

Result:
  1. CSS file served directly from dist folder
  2. Browser applies styles
  3. No JavaScript execution needed
```

## Why Order Matters

### Correct Order (Current Configuration)

```
1. /api/(.*)                 ← Most specific
2. /assets/(.*)              ← Specific
3. /track_maps/(.*)          ← Specific
4. /vite.svg                 ← Very specific
5. /(.*)\.(ext)             ← Semi-specific (file extension)
6. /(.*)                     ← Catch-all (LAST!)
```

**Result:** Everything works! API calls route to backend, assets load, React Router handles navigation.

### Wrong Order (Example of What NOT to Do)

```
1. /(.*)                     ← Catch-all (FIRST - BAD!)
2. /api/(.*)                 ← Never reached!
3. /assets/(.*)              ← Never reached!
```

**Result:** ALL requests match route 1, serve index.html:
- API calls return HTML instead of JSON → JavaScript errors
- Asset requests return HTML instead of JS/CSS → Page broken
- Nothing works!

## Build Output Structure

```
frontend/dist/
├── index.html           → Entry point for all SPA routes
├── vite.svg            → Vite logo
├── assets/
│   ├── index-DhxXsaDh.js   → React app bundle (main)
│   └── index-Bnz4PAGb.css  → Styles
└── track_maps/
    ├── monaco.svg      → Track layouts
    └── spa.svg
```

This structure is served from `/frontend/dist/` in Vercel.

## Frontend vs Backend Separation

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Vercel App                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────┐   ┌────────────────────────┐  │
│  │     Frontend (React)    │   │   Backend (FastAPI)    │  │
│  │                         │   │                        │  │
│  │  - Static files         │   │  - Serverless function │  │
│  │  - React Router         │   │  - API endpoints       │  │
│  │  - Client-side logic    │   │  - Database queries    │  │
│  │  - UI components        │   │  - AI integration      │  │
│  │                         │   │                        │  │
│  │  Served from:           │   │  Executed at:          │  │
│  │  /frontend/dist/*       │   │  /backend/api/index.py │  │
│  │                         │   │                        │  │
│  │  Routes:                │   │  Routes:               │  │
│  │  /, /scout, /overview   │   │  /api/*                │  │
│  └─────────────────────────┘   └────────────────────────┘  │
│              │                           │                  │
│              └───────── Communicate ─────┘                  │
│                     via HTTP/JSON                           │
└─────────────────────────────────────────────────────────────┘
```

## React Router Integration

```
User Types URL: /scout/driver/1/overview
                      |
                      v
            ┌─────────────────────┐
            │  Browser Request    │
            │  to Vercel          │
            └─────────────────────┘
                      |
                      v
            ┌─────────────────────┐
            │  Vercel Routes      │
            │  (vercel.json)      │
            └─────────────────────┘
                      |
                      v
            ┌─────────────────────┐
            │  No route matches   │
            │  Catch-all: /(.*)   │
            └─────────────────────┘
                      |
                      v
            ┌─────────────────────┐
            │  Serve index.html   │
            └─────────────────────┘
                      |
                      v
            ┌─────────────────────┐
            │  Browser loads HTML │
            │  Executes React     │
            └─────────────────────┘
                      |
                      v
            ┌─────────────────────┐
            │  React Router reads │
            │  URL from browser   │
            │  window.location    │
            └─────────────────────┘
                      |
                      v
            ┌─────────────────────┐
            │  Routes config in   │
            │  App.jsx matches:   │
            │  /scout/driver/:id  │
            └─────────────────────┘
                      |
                      v
            ┌─────────────────────┐
            │  Render Overview    │
            │  component with     │
            │  params.id = "1"    │
            └─────────────────────┘
```

## Key Takeaways

1. **Route Order is Critical**: Specific routes before generic routes
2. **Catch-all Must Be Last**: SPA routing depends on this
3. **API Routes First**: Prevent HTML being served instead of JSON
4. **Asset Routes Explicit**: Ensure all file types are covered
5. **One HTML, Many Routes**: React Router handles all page navigation
6. **Backend is Separate**: API runs as serverless function, not part of static site

## Debugging Tips

If routes don't work:
1. Check Vercel logs: Which route matched?
2. Check Network tab: What was served?
3. Check Console: Any React Router errors?
4. Verify catch-all is LAST in vercel.json
5. Rebuild frontend if assets changed

---

**Visual Architecture by:** Claude
**Date:** November 3, 2025
