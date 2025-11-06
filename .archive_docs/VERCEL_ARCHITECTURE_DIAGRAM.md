# Vercel Deployment Architecture - Visual Diagram

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VERCEL CLOUD PLATFORM                              │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                      EDGE NETWORK (CDN)                                 │ │
│  │  • Global distribution                                                  │ │
│  │  • Static asset caching                                                 │ │
│  │  • Request routing                                                      │ │
│  └─────────────┬──────────────────────────────────┬────────────────────────┘ │
│                │                                   │                          │
│                ▼                                   ▼                          │
│  ┌─────────────────────────┐       ┌──────────────────────────────┐         │
│  │   STATIC FRONTEND       │       │   SERVERLESS FUNCTIONS       │         │
│  │   /frontend/dist        │       │   /api/index.py              │         │
│  ├─────────────────────────┤       ├──────────────────────────────┤         │
│  │ • index.html            │       │ Runtime: Python 3.9          │         │
│  │ • React bundles (.js)   │       │ Memory: 1024 MB              │         │
│  │ • CSS files             │       │ Timeout: 30s                 │         │
│  │ • Static assets         │       │                              │         │
│  │                         │       │ ┌─────────────────────────┐  │         │
│  │ Served from Edge CDN    │       │ │   FastAPI Application   │  │         │
│  │ (instant delivery)      │       │ │   /backend/main.py      │  │         │
│  │                         │       │ └─────────────────────────┘  │         │
│  └─────────────────────────┘       └──────────────────────────────┘         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ API Requests
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐  │
│  │   SNOWFLAKE DB       │  │   ANTHROPIC API      │  │  LOCAL JSON      │  │
│  │   (Primary Data)     │  │   (AI Coaching)      │  │  (Fallback)      │  │
│  ├──────────────────────┤  ├──────────────────────┤  ├──────────────────┤  │
│  │ • Telemetry data     │  │ • Claude AI model    │  │ • Cached data    │  │
│  │ • 40GB+ historical   │  │ • Strategy insights  │  │ • /data/*.json   │  │
│  │ • Real-time updates  │  │ • Coaching advice    │  │ • Backup source  │  │
│  │ • RSA key auth       │  │ • API key auth       │  │ • Always works   │  │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Request Flow - Static Content

```
User Browser
    │
    │ GET https://your-app.vercel.app/
    │
    ▼
┌─────────────────────────────────────┐
│   Vercel Edge Network (CDN)         │
│   • Checks cache                    │
│   • Serves static files instantly   │
└─────────────────────────────────────┘
    │
    │ Cached Response (< 50ms)
    │
    ▼
┌─────────────────────────────────────┐
│   Browser receives:                 │
│   • index.html                      │
│   • React bundles                   │
│   • CSS                             │
│   • Client-side routing enabled     │
└─────────────────────────────────────┘
```

## 3. Request Flow - API Calls

```
Browser (React App)
    │
    │ POST /api/chat
    │ { message: "How can I improve?", driver: 13 }
    │
    ▼
┌─────────────────────────────────────────────────┐
│   Vercel Routing Layer                          │
│   Rewrites: /api/* → /api/index                 │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│   Serverless Function: /api/index.py            │
│   ┌──────────────────────────────────────────┐  │
│   │  1. Cold Start (if needed)               │  │
│   │     - Load Python runtime                │  │
│   │     - Install dependencies               │  │
│   │     - Import FastAPI app                 │  │
│   │     (Cached after first invocation)      │  │
│   └──────────────────────────────────────────┘  │
│   ┌──────────────────────────────────────────┐  │
│   │  2. Request Processing                   │  │
│   │     - Mangum adapts ASGI → Lambda        │  │
│   │     - Routes to FastAPI app              │  │
│   │     - Executes business logic            │  │
│   └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│   FastAPI Application                           │
│   /backend/main.py → app/api/routes.py          │
│   ┌──────────────────────────────────────────┐  │
│   │  Route Handler: POST /chat               │  │
│   │  ├─ Validate request (Pydantic)          │  │
│   │  ├─ Load driver data                     │  │
│   │  ├─ Load track data                      │  │
│   │  └─ Call AI service                      │  │
│   └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│   AI Strategy Service                           │
│   /backend/app/services/ai_strategy.py          │
│   ┌──────────────────────────────────────────┐  │
│   │  generate_coaching()                     │  │
│   │  ├─ Build context from driver/track     │  │
│   │  ├─ Format prompt for Claude            │  │
│   │  └─ Send to Anthropic API               │  │
│   └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│   Anthropic API (External)                      │
│   https://api.anthropic.com/v1/messages         │
│   ┌──────────────────────────────────────────┐  │
│   │  Claude AI Processing                    │  │
│   │  • Analyzes driver skills                │  │
│   │  • Generates coaching advice             │  │
│   │  • Returns natural language response     │  │
│   └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
    │
    │ Response flows back through layers
    │
    ▼
Browser receives JSON:
{
  "message": "Focus on corner entry speed...",
  "suggested_questions": [...]
}
```

## 4. Data Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA RELIABILITY SERVICE                      │
│              /backend/app/services/data_reliability_service.py   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ get_telemetry_data()
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
    │   TIER 1         │ │   TIER 2     │ │   TIER 3     │
    │   Snowflake      │ │   JSON Files │ │   Cache      │
    └──────────────────┘ └──────────────┘ └──────────────┘
            │                    │               │
            │ Try first          │ Fallback      │ Memory
            │                    │               │
            ▼                    ▼               ▼
    ┌──────────────────────────────────────────────────┐
    │  Automatic Failover Logic                        │
    │  ┌────────────────────────────────────────────┐  │
    │  │ IF Snowflake fails:                        │  │
    │  │   → Try local JSON                         │  │
    │  │      IF JSON fails:                        │  │
    │  │        → Try cache                         │  │
    │  │           IF cache empty:                  │  │
    │  │             → Return error                 │  │
    │  │                                            │  │
    │  │ Health Status:                             │  │
    │  │ • All working: "healthy"                   │  │
    │  │ • Snowflake down: "degraded"               │  │
    │  │ • All down: "critical"                     │  │
    │  └────────────────────────────────────────────┘  │
    └──────────────────────────────────────────────────┘
```

## 5. Frontend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    REACT APPLICATION                             │
│                    /frontend/src/                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
    ┌──────────────────────┐       ┌──────────────────────┐
    │   Context Providers   │       │   Routing Layer      │
    │   (Global State)      │       │   (React Router)     │
    ├──────────────────────┤       ├──────────────────────┤
    │ • DriverContext      │       │ /scout               │
    │ • ScoutContext       │       │ /scout/driver/:id/*  │
    │ • SelectionContext   │       │ /overview            │
    └──────────────────────┘       │ /skills              │
                │                   │ /improve             │
                │                   └──────────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
    ┌──────────────────────┐       ┌──────────────────────┐
    │   Page Components     │       │   API Service        │
    ├──────────────────────┤       ├──────────────────────┤
    │ • ScoutLanding       │       │ services/api.js      │
    │ • Overview           │       │ ┌──────────────────┐ │
    │ • Skills             │───────│▶│ fetch API calls  │ │
    │ • Improve            │       │ │ • /api/drivers   │ │
    │ • RaceLog            │       │ │ • /api/telemetry │ │
    └──────────────────────┘       │ │ • /api/chat      │ │
                                   │ └──────────────────┘ │
                                   └──────────────────────┘
```

## 6. Backend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI APPLICATION                           │
│                    /backend/main.py                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ include_router()
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API ROUTER                                    │
│                    /backend/app/api/routes.py                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Endpoints:                          Models:                    │
│  ┌────────────────────────┐         ┌──────────────────────┐   │
│  │ GET  /tracks           │────────▶│ Track                │   │
│  │ GET  /drivers          │         │ Driver               │   │
│  │ POST /predict          │         │ CircuitFitPrediction │   │
│  │ POST /chat             │         │ ChatRequest          │   │
│  │ GET  /telemetry/*      │         │ TelemetryComparison  │   │
│  │ GET  /health           │         └──────────────────────┘   │
│  └────────────────────────┘                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
    │   Data Loader    │ │  AI Service  │ │  Telemetry   │
    │   Service        │ │  Service     │ │  Service     │
    ├──────────────────┤ ├──────────────┤ ├──────────────┤
    │ • Load drivers   │ │ • Generate   │ │ • Process    │
    │ • Load tracks    │ │   coaching   │ │   lap data   │
    │ • Calculate fit  │ │ • Format     │ │ • Compare    │
    │ • Get stats      │ │   prompts    │ │   drivers    │
    └──────────────────┘ └──────────────┘ └──────────────┘
            │                    │               │
            │                    │               │
            └────────────────────┴───────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │ Data Reliability     │
                    │ Service              │
                    │ (Multi-tier failover)│
                    └──────────────────────┘
```

## 7. CORS Configuration Flow

```
Browser (React)                      FastAPI Backend
    │                                        │
    │ Preflight OPTIONS /api/drivers        │
    ├───────────────────────────────────────▶│
    │                                        │
    │                     Check CORS config  │
    │                     ┌──────────────────┤
    │                     │ allowed_origins: │
    │                     │ • localhost:5173 │
    │                     │ • *.vercel.app   │
    │                     └──────────────────┤
    │                                        │
    │ ◀───────────────────────────────────────┤
    │ 200 OK                                 │
    │ Access-Control-Allow-Origin: *         │
    │ Access-Control-Allow-Methods: *        │
    │ Access-Control-Allow-Headers: *        │
    │                                        │
    │ GET /api/drivers (actual request)      │
    ├───────────────────────────────────────▶│
    │                                        │
    │ ◀───────────────────────────────────────┤
    │ 200 OK + CORS headers + JSON data      │
    │                                        │
```

## 8. Environment Variables Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    VERCEL DASHBOARD                              │
│                    Settings → Environment Variables              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ANTHROPIC_API_KEY=sk-ant-xxxxx         ┐                       │
│  SNOWFLAKE_ACCOUNT=EOEPNYL-PR46214      │                       │
│  SNOWFLAKE_USER=hackthetrack_svc        │ Encrypted Storage    │
│  SNOWFLAKE_PRIVATE_KEY=<base64>         │                       │
│  ...                                    ┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Injected at runtime
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              SERVERLESS FUNCTION RUNTIME                         │
│              (Isolated container per invocation)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  os.environ['ANTHROPIC_API_KEY']  ───▶  anthropic.Client()     │
│  os.environ['SNOWFLAKE_ACCOUNT']  ───▶  snowflake.connect()    │
│  os.environ['USE_SNOWFLAKE']      ───▶  data source selection  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 9. Build & Deploy Pipeline

```
Local Development
    │
    │ git push origin master
    │
    ▼
┌─────────────────────────────────────────┐
│   GitHub Repository                     │
│   (Source of truth)                     │
└─────────────────────────────────────────┘
    │
    │ Webhook trigger
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VERCEL BUILD SYSTEM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: Clone Repository                                       │
│  ├─ git clone https://github.com/user/repo                      │
│  └─ Checkout: master branch                                     │
│                                                                  │
│  Step 2: Frontend Build                                         │
│  ├─ cd frontend                                                 │
│  ├─ npm ci                          (Install dependencies)      │
│  ├─ npm run build                   (Vite build)                │
│  └─ Output: frontend/dist/                                      │
│                                                                  │
│  Step 3: Backend Setup                                          │
│  ├─ Detect Python runtime                                       │
│  ├─ Install: api/requirements.txt                               │
│  └─ Create: /api/index function                                 │
│                                                                  │
│  Step 4: Deploy to Edge                                         │
│  ├─ Upload static files to CDN                                  │
│  ├─ Deploy serverless functions                                 │
│  └─ Configure routing rules                                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
    │
    │ Build complete (2-3 minutes)
    │
    ▼
┌─────────────────────────────────────────┐
│   LIVE DEPLOYMENT                       │
│   https://your-app.vercel.app           │
│   • Static assets on CDN                │
│   • Serverless functions ready          │
│   • Health check: /api/health           │
└─────────────────────────────────────────┘
```

## 10. Cold Start vs. Warm Start

```
COLD START (First invocation or after idle)
────────────────────────────────────────────

Request arrives
    │
    ▼
┌─────────────────────────────────┐
│ 1. Provision container          │  ~500ms
│    - Allocate resources          │
│    - Setup Python runtime        │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ 2. Install dependencies          │  ~2-3s
│    - pip install requirements    │
│    - Import modules              │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ 3. Initialize application        │  ~500ms
│    - Load FastAPI app            │
│    - Setup routes                │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ 4. Process request               │  ~100-500ms
│    - Execute handler             │
│    - Return response             │
└─────────────────────────────────┘

Total: ~3-4 seconds


WARM START (Container reused)
──────────────────────────────

Request arrives
    │
    ▼
┌─────────────────────────────────┐
│ Container already ready          │
│ - Python runtime loaded          │
│ - Dependencies imported          │
│ - App initialized                │
└─────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────┐
│ Process request                  │  ~100-500ms
│ - Execute handler                │
│ - Return response                │
└─────────────────────────────────┘

Total: ~100-500ms
```

## 11. Error Handling Flow

```
Request
    │
    ▼
┌─────────────────────────────────────────┐
│   Vercel Function Entry Point           │
│   try:                                  │
│     return handler(event, context)      │
│   except Exception as e:                │
│     log_error(e)                        │
│     return 500 response                 │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│   FastAPI Exception Handlers            │
│   • HTTPException → 4xx/5xx             │
│   • ValidationError → 422               │
│   • Exception → 500                     │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│   Service Layer Error Handling          │
│   • DataUnavailableError → Failover     │
│   • SnowflakeError → Try JSON           │
│   • APIError → Log and raise            │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│   Frontend Error Display                │
│   • Show user-friendly message          │
│   • Log to console (dev mode)           │
│   • Retry mechanism                     │
└─────────────────────────────────────────┘
```

## 12. Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 1: Vercel Platform                                       │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ • DDoS protection                                      │    │
│  │ • Rate limiting                                        │    │
│  │ • SSL/TLS encryption (automatic)                       │    │
│  │ • Edge firewall                                        │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Layer 2: Application (FastAPI)                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ • CORS policy enforcement                              │    │
│  │ • Input validation (Pydantic)                          │    │
│  │ • Request size limits                                  │    │
│  │ • Authentication headers                               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Layer 3: Secrets Management                                    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ • Encrypted environment variables                      │    │
│  │ • No secrets in code                                   │    │
│  │ • Base64 encoding for keys                             │    │
│  │ • Least privilege access                               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Layer 4: Data Access                                           │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ • Snowflake RSA key authentication                     │    │
│  │ • Anthropic API key validation                         │    │
│  │ • Read-only database access                            │    │
│  │ • No user input in SQL queries                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary

This architecture provides:

✅ **Scalability** - Serverless functions scale automatically
✅ **Reliability** - Multi-tier data failover
✅ **Performance** - Edge CDN for static content, warm container reuse
✅ **Security** - Multiple security layers, encrypted secrets
✅ **Maintainability** - Clear separation of concerns
✅ **Cost-Efficiency** - Pay only for function execution time

**Key Metrics:**
- Cold start: ~3-4 seconds
- Warm start: ~100-500ms
- Static content delivery: < 50ms (CDN)
- Frontend bundle: 856 KB (optimization recommended)
- Backend memory: 1024 MB
- Function timeout: 30 seconds

**Deployment Ready After:** Applying 3 critical fixes from DEPLOYMENT_FIXES_PRIORITY.md
