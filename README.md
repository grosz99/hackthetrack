# Gibbs AI 🏁

**"Making the Predictable Unpredictable"**

An AI-powered racing talent scouting and development platform that replicates Joe Gibbs Racing's legendary eye for talent. Built on the validated 4-Factor Performance Model (R² = 0.895), Gibbs AI helps identify and develop the drivers of the future—just as Joe Gibbs has done for decades in NASCAR and the NFL.

---

## 🎯 Core Features

### Driver Rankings & Scouting
- **Global Rankings**: Complete driver standings based on the 4-Factor Model
- **Toyota Gibbs Branding**: Professional racing team aesthetic
- **Sortable Metrics**: Speed, Consistency, Racecraft, Tire Management
- **Click-Through Profiles**: Deep dive into any driver's performance

### Driver Performance Dashboard (5 Pages)
1. **Overview**: Complete performance snapshot with 4-factor breakdown
2. **Race Log**: Season-by-season race results with filtering
3. **Skills Analysis**: AI-powered scouting reports for each factor
4. **Development/Improve**: Personalized improvement recommendations
5. **Practice Plan Generator**: AI-driven training programs

### AI Coaching Intelligence
- **Factor-Specific Coaching**: AI analysis for Speed, Consistency, Racecraft, Tire Management
- **Comparative Insights**: How to improve by learning from better drivers
- **Practice Plan Generator**: Personalized track-specific training programs
- **Claude 3.5 Sonnet**: Real AI-powered coaching, not templates

### The 4-Factor Performance Model
Validated statistical model explaining 89.5% of race outcomes:
- **Speed (46.6%)**: Raw pace through lap times and sector performance
- **Consistency (29.1%)**: Lap-to-lap repeatability and variation control
- **Racecraft (14.9%)**: Wheel-to-wheel skills and overtaking efficiency
- **Tire Management (9.5%)**: Pace preservation over race distance

---

## 🏗️ Architecture

### Production Deployment

```
┌─────────────────────────────────────────────────────────┐
│                    USER ACCESS                           │
│         https://gibbs-ai.netlify.app                     │
│         (Publicly accessible, no authentication)         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ React SPA
                     ↓
┌─────────────────────────────────────────────────────────┐
│              FRONTEND (Netlify)                          │
│  - React 19 + Vite                                       │
│  - Client-side routing (React Router v7)                 │
│  - Toyota Gibbs Racing branding                          │
│  - No authentication required                            │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ HTTPS/JSON
                     │ CORS-enabled
                     ↓
┌─────────────────────────────────────────────────────────┐
│              BACKEND API (Heroku)                        │
│  https://hackthetrack-api-ae28ad6f804d.herokuapp.com     │
│                                                           │
│  - FastAPI (Python 3.12)                                 │
│  - Docker containerized                                  │
│  - JSON file-based data (no database)                    │
│  - Anthropic Claude API integration                      │
└─────────────────────────────────────────────────────────┘
```

### Backend Structure
```
backend/
├── app/
│   ├── api/
│   │   └── routes.py                    # All API endpoints
│   ├── services/
│   │   ├── data_loader.py               # JSON data loading & caching
│   │   ├── ai_skill_coach.py            # Anthropic factor coaching
│   │   ├── ai_practice_planner.py       # Practice plan generation
│   │   ├── factor_analyzer.py           # 4-factor analysis
│   │   └── improve_predictor.py         # Performance predictions
│   └── models.py                        # Pydantic data models
├── data/                                # All race data (JSON files)
│   ├── driver_factors.json              # 4-factor scores
│   ├── driver_race_results.json         # Season results
│   ├── factor_breakdowns.json           # Factor detail breakdowns
│   ├── coaching_recommendations.json    # Pre-cached coaching data
│   └── track_layouts.json               # Track configurations
├── main.py                              # FastAPI application
├── Dockerfile                           # Heroku deployment config
└── requirements.txt                     # Python dependencies
```

### Frontend Structure
```
frontend/
├── src/
│   ├── pages/
│   │   ├── Rankings/Rankings.jsx        # Main driver rankings page
│   │   ├── Overview/Overview.jsx        # Driver overview dashboard
│   │   ├── RaceLog/RaceLog.jsx          # Race results history
│   │   ├── Skills/Skills.jsx            # AI skill analysis
│   │   └── Improve/Improve.jsx          # Improvement recommendations
│   ├── components/
│   │   ├── WelcomeModal/                # Onboarding tutorial
│   │   ├── ToyotaGibbsLogo/             # Branding components
│   │   ├── RankingsTable/               # Driver rankings table
│   │   ├── DashboardHeader/             # Page headers
│   │   └── CoachRecommendations/        # AI coaching display
│   ├── contexts/
│   │   └── DriverContext.jsx            # Global driver state
│   ├── services/
│   │   └── api.js                       # Backend API client
│   ├── App.jsx                          # React Router setup
│   └── main.jsx                         # React entry point
├── public/
│   └── assets/                          # Images and logos
├── netlify.toml                         # Netlify deployment config
└── package.json                         # Node dependencies
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- Anthropic API key ([get one here](https://console.anthropic.com/))

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
   PORT=8000
   ```

5. **Run the backend**:
   ```bash
   python main.py
   ```

   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   Create `.env.local`:
   ```
   VITE_API_URL=http://localhost:8000
   ```

4. **Run the frontend**:
   ```bash
   npm run dev
   ```

   Frontend will be available at `http://localhost:5173`

### Access the Application

Open your browser and navigate to `http://localhost:5173`

---

## 📦 Production Deployment

### Frontend Deployment (Netlify)

**Current Production URL**: https://gibbs-ai.netlify.app

#### Netlify Configuration
The frontend deploys automatically when you push to GitHub master branch.

**Configuration file**: `netlify.toml`
```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "frontend/dist"

[build.environment]
  NODE_VERSION = "18"
  VITE_API_URL = "https://hackthetrack-api-ae28ad6f804d.herokuapp.com"
```

**Benefits**:
- ✅ Public by default (no authentication required)
- ✅ Automatic HTTPS
- ✅ CDN distribution
- ✅ Automatic preview deployments for PRs
- ✅ Free tier sufficient

#### Manual Deployment (if needed)
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd frontend
netlify deploy --prod
```

### Backend Deployment (Heroku)

**Current Production URL**: https://hackthetrack-api-ae28ad6f804d.herokuapp.com

#### Heroku Configuration
The backend uses Docker deployment via `heroku.yml`:

```yaml
build:
  docker:
    web: backend/Dockerfile
run:
  web: python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### Environment Variables (Heroku)
Set these in the Heroku dashboard or via CLI:
```bash
heroku config:set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here --app hackthetrack-api
heroku config:set FRONTEND_URL=https://gibbs-ai.netlify.app --app hackthetrack-api
```

#### Deploy to Heroku
```bash
# Push to Heroku (from repository root)
git push heroku master

# Or force push if needed
git push heroku master --force

# Check deployment logs
heroku logs --tail --app hackthetrack-api

# Restart if needed
heroku restart --app hackthetrack-api
```

#### Heroku Stack
- **Stack**: `container` (Docker-based)
- **Runtime**: Python 3.12 (specified in Dockerfile)
- **Web server**: Uvicorn (ASGI server for FastAPI)

---

## 📊 API Endpoints

### Core Data Endpoints
- `GET /api/drivers` - Get all drivers with 4-factor profiles
- `GET /api/drivers/{driver_number}` - Get specific driver details
- `GET /api/drivers/{driver_number}/season` - Get season statistics
- `GET /api/drivers/{driver_number}/results` - Get race-by-race results
- `GET /api/tracks` - Get all tracks
- `GET /api/health` - API health check

### AI Coaching Endpoints
- `GET /api/factors/{factor}/coaching/{driver_number}` - Get AI coaching for specific factor
  - Factors: `speed`, `consistency`, `racecraft`, `tire_management`
- `POST /api/coaching/comparative-insights` - Get comparative coaching insights
  ```json
  {
    "current_driver_number": 7,
    "comparable_driver_number": 13,
    "factor_name": "speed",
    "improvement_delta": 15.5,
    "track_name": "Barber Motorsports Park"
  }
  ```
- `POST /api/practice-plan` - Generate personalized practice plan
  ```json
  {
    "driver_number": 7,
    "track_name": "Barber Motorsports Park",
    "weak_factors": ["tire_management", "consistency"]
  }
  ```

### Analysis Endpoints
- `GET /api/drivers/{driver_number}/skill-gaps` - Calculate improvement opportunities
- `GET /api/drivers/{driver_number}/similar` - Find similar drivers for comparison
- `GET /api/factors/{factor}/stats` - Get factor statistics across all drivers

---

## 🔑 Key Technologies

### Backend
- **FastAPI**: Modern Python API framework with automatic OpenAPI docs
- **Anthropic SDK**: Claude 3.5 Sonnet (claude-sonnet-4-5-20250929) integration
- **Pandas**: Data manipulation and analysis
- **Pydantic v2**: Data validation and settings management
- **Docker**: Containerization for Heroku deployment
- **Uvicorn**: High-performance ASGI server

### Frontend
- **React 19**: Modern UI framework with hooks
- **React Router v7**: Client-side routing with nested routes
- **Vite**: Fast build tool and dev server
- **Framer Motion**: Smooth animations and transitions
- **CSS Modules**: Scoped styling per component

### Infrastructure
- **Netlify**: Frontend hosting with automatic deployments
- **Heroku**: Backend API hosting with Docker containers
- **GitHub**: Version control and CI/CD trigger
- **Anthropic API**: AI coaching and insights generation

---

## 🎨 Design System

### Color Palette (Toyota Gibbs Racing)
- **Primary Red**: `#EB0A1E` (Toyota GR branding)
- **Dark Red**: `#B80818` (Darker accent)
- **Dark Background**: `#1a1a1a` (Page backgrounds)
- **Card Background**: `#2a2a2a` (Component backgrounds)
- **Text Primary**: `#ffffff` (Headings)
- **Text Secondary**: `#a0a0a0` (Body text)
- **Success**: `#00C853` (Positive metrics)
- **Warning**: `#FFA000` (Mid-range metrics)
- **Danger**: `#ff3b30` (Negative metrics)

### Typography
- **Font Family**: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Headings**: 600-700 weight
- **Body**: 400-500 weight
- **Monospace**: Used for driver numbers and stats

### Component Styling
- **Border Radius**: 8-12px (modern, rounded corners)
- **Shadows**: Subtle depth with `rgba(0, 0, 0, 0.3)`
- **Animations**: Framer Motion for smooth transitions
- **Responsive**: Mobile-first design with breakpoints

---

## 📈 The 4-Factor Performance Model

### Statistical Validation
- **R² = 0.895** (explains 89.5% of race finish variance)
- **MAE = 1.78 positions** (average prediction error)
- **Validated on**: 291 driver-race observations across 12 races
- **34 drivers** analyzed in Toyota GR86 Cup series

### Factor Weights (Regression Coefficients)
1. **Speed**: 46.6% influence on finish position
2. **Consistency**: 29.1% influence
3. **Racecraft**: 14.9% influence
4. **Tire Management**: 9.5% influence

### Factor Definitions

**Speed** - Raw pace capability
- Measures: Fastest lap times, qualifying performance, sector times
- Indicates: Pure driving speed when pushing to the limit

**Consistency** - Performance repeatability
- Measures: Lap time standard deviation, sector variation
- Indicates: Ability to reproduce best performance lap after lap

**Racecraft** - Wheel-to-wheel skills
- Measures: Overtaking efficiency, position changes, defensive positioning
- Indicates: Race execution under pressure and competitive situations

**Tire Management** - Pace preservation
- Measures: Early vs. late lap time degradation, long-run pace
- Indicates: Ability to maintain speed as tires wear

---

## 🧪 Testing

### Backend API Tests
```bash
cd backend
pytest tests/ -v
```

**Test Coverage**: Comprehensive endpoint validation

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 📝 Data Architecture

### Single Source of Truth
All race data is stored in JSON files located in `backend/data/`:

- **driver_factors.json** (208 KB) - 4-factor scores for all 34 drivers
- **driver_race_results.json** (295 KB) - Complete season race results
- **driver_season_stats.json** (11 KB) - Aggregated season statistics
- **factor_breakdowns.json** (116 KB) - Detailed factor component data
- **coaching_recommendations.json** (6 KB) - Pre-calculated coaching insights
- **track_layouts.json** (27 KB) - Track configurations and corner data

### Data Loading Strategy
- **In-Memory Cache**: All data loaded on backend startup
- **No Database**: Zero query latency, instant responses
- **JSON Parsing**: Fast Python json module
- **Singleton Pattern**: Data loaded once, reused for all requests

### Updating Production Data
1. Edit JSON files in `backend/data/`
2. Commit and push to GitHub master branch
3. Deploy to Heroku: `git push heroku master`
4. Heroku restarts automatically and loads new data
5. Frontend automatically uses updated data through API

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

**Development Guidelines**:
- Keep functions under 50 lines
- Add tests for new features
- Follow existing code style
- Update README for new features

---

## 🙏 Acknowledgments

### Inspiration
- **Joe Gibbs Racing**: Legendary talent development in NASCAR
- **PFF.com**: Analytics presentation and scouting approach
- **DataGolf.com**: Statistical modeling methodology
- **VRS.racing**: Telemetry comparison concepts

### Technology
- **Anthropic Claude**: AI-powered coaching intelligence
- **Toyota GR86 Cup**: Racing series data and inspiration
- **Netlify**: Reliable frontend hosting
- **Heroku**: Stable backend infrastructure

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Check deployment docs in `NETLIFY_DEPLOYMENT.md`

---

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ for motorsports talent development**

*"Your finish is 89% predictable — let's change that."*
