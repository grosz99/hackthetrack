# Racing Analytics Platform 🏁

**"Making the Predictable Unpredictable"**

A 3-page AI-powered racing analytics platform that leverages the validated 4-Factor Model (R² = 0.895) to provide track intelligence, strategy coaching, and telemetry comparison tools for Toyota GR86 spec racing series.

---

## 🎯 Features

### Page 1: Track Intelligence
- **Track Selection**: Choose from 6 tracks (Barber, COTA, Road America, Sebring, Sonoma, VIR)
- **Spider Graph**: Visualize track demand profiles across 4 skill dimensions
- **Driver Rankings**: See predicted performance based on circuit fit scores
- **Skill Breakdown**: Understand each driver's strengths and weaknesses

### Page 2: AI Strategy Coach
- **Anthropic Claude Integration**: Chat with AI strategist powered by Claude 3.5 Sonnet
- **Context-Aware Insights**: AI knows your driver profile and track demands
- **Actionable Strategy**: Get specific race-day guidance based on data
- **Suggested Questions**: Pre-built prompts to explore key topics

### Page 3: Telemetry Comparison
- **Lap-by-Lap Analysis**: Compare your performance against any driver
- **Sector Deltas**: Identify exactly where time is gained/lost
- **Visual Charts**: Line charts and bar graphs showing performance gaps
- **Key Insights**: AI-generated recommendations on improvement areas

---

## 🏗️ Architecture

### Backend (Python FastAPI)
```
backend/
├── app/
│   ├── api/
│   │   └── routes.py               # All API endpoints (1,192 lines)
│   ├── services/
│   │   ├── data_loader.py          # JSON/CSV data loading & caching
│   │   ├── snowflake_service.py    # Snowflake integration (270 lines, simplified)
│   │   ├── ai_strategy.py          # Anthropic Claude strategy chat
│   │   ├── ai_telemetry_coach.py   # Anthropic telemetry coaching
│   │   ├── telemetry_processor.py  # Telemetry data processing
│   │   ├── factor_analyzer.py      # 4-factor analysis
│   │   ├── race_log_processor.py   # Race result processing
│   │   └── improve_predictor.py    # Performance improvement predictions
│   ├── models.py                   # Pydantic data models
│   └── __init__.py
├── tests/
│   ├── test_api_endpoints.py       # 22 comprehensive endpoint tests
│   ├── test_deployment_validation.py
│   └── conftest.py
├── main.py                         # FastAPI application
├── requirements.txt                # Python dependencies
└── .env.example                    # Environment variables template
```

### Frontend (React + Vite)
```
frontend/
├── src/
│   ├── pages/
│   │   ├── TrackIntelligence.jsx    # Page 1
│   │   ├── StrategyChat.jsx          # Page 2
│   │   └── TelemetryComparison.jsx   # Page 3
│   ├── components/
│   │   └── Navigation.jsx            # Main navigation bar
│   ├── services/
│   │   └── api.js                    # API client
│   ├── data/
│   │   └── dashboardData.json        # Pre-calculated driver/track data
│   ├── App.jsx                       # React Router setup
│   └── main.jsx                      # React entry point
├── package.json
└── .env.example                     # Frontend environment variables
```

---

## 🚀 Quick Start

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
   ANTHROPIC_API_KEY=your_api_key_here
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
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
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

## 📊 API Endpoints

### Tracks
- `GET /api/tracks` - Get all tracks with demand profiles
- `GET /api/tracks/{track_id}` - Get specific track

### Drivers
- `GET /api/drivers` - Get all drivers with skill profiles
- `GET /api/drivers?track_id={track_id}` - Get drivers with circuit fit for track
- `GET /api/drivers/{driver_number}` - Get specific driver

### Predictions
- `POST /api/predict` - Predict driver performance at track
  ```json
  {
    "driver_number": 13,
    "track_id": "cota"
  }
  ```

### AI Chat
- `POST /api/chat` - Send message to AI strategy coach
  ```json
  {
    "message": "What should I focus on at Road America?",
    "driver_number": 13,
    "track_id": "roadamerica",
    "history": []
  }
  ```

### Telemetry
- `GET /api/telemetry/compare?track_id={id}&driver_1={num}&driver_2={num}&race_num={1|2}`
  - Compare lap-by-lap data between two drivers

### Health
- `GET /api/health` - Check API health and data loading status

---

## 🎨 Design Principles

### Color Palette
- **Primary Red**: `#EB0A1E` (GR branding)
- **Dark**: `#1d1d1f` (text)
- **Mid Gray**: `#86868b` (secondary text)
- **Light Gray**: `#e5e5e7` (borders)
- **White**: `#ffffff` (backgrounds)
- **Success Green**: `#34C759` (positive deltas)

### Typography
- **System Font Stack**: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto
- **Headings**: 600-700 weight
- **Body**: 400-500 weight

### Layout
- **Max Width**: 1400-1600px
- **Border Radius**: 8-16px (modern, rounded)
- **Shadows**: Subtle elevation (0 2px 8px rgba(0,0,0,0.05))

---

## 🧪 Testing

### Backend Tests
The backend has a comprehensive test suite with **20/20 tests passing (100%)**:

```bash
cd backend
pytest tests/test_api_endpoints.py -v
```

**Test Coverage:**
- ✅ Health & Root endpoints (2/2)
- ✅ Track endpoints (3/3)
- ✅ Driver endpoints (6/6)
- ✅ Prediction endpoints (2/2)
- ✅ Telemetry endpoints (3/3)
- ✅ Factor analysis endpoints (2/2)
- ✅ Driver improvement endpoints (2/2)

### Frontend Tests
```bash
cd frontend
npm test
```

### Code Quality
- **Simplified Architecture**: Reduced data service code by 72% (956 → 270 lines)
- **Direct Query Pattern**: Eliminated complex 3-layer failover for faster responses
- **100% Test Success Rate**: All API endpoints validated and working
- **Clean Documentation**: Streamlined from 50+ markdown files to 3 essential docs

---

## 📦 Deployment

### Current Production URLs
- **Frontend**: Auto-deployed to Vercel (https://circuit-fbtth1gml-justin-groszs-projects.vercel.app)
- **Backend API**: Heroku (https://hackthetrack-api-ae28ad6f804d.herokuapp.com)

### Data Architecture
**Single Source of Truth**: JSON files in `backend/data/`
- `dashboardData.json` - Driver/track overview
- `driver_factors.json` - Factor scores for all 34 drivers
- `driver_season_stats.json` - Season statistics
- `driver_race_results.json` - Race-by-race results

All data is loaded into memory on startup. **No database queries** - responses are instant!

### Backend Deployment (Heroku)

1. **Set environment variables** on Heroku:
   ```bash
   heroku config:set ANTHROPIC_API_KEY=your_key -a hackthetrack-api
   heroku config:set CORS_ALLOW_ALL=true -a hackthetrack-api
   ```

2. **Deploy using git subtree** (backend is in subdirectory):
   ```bash
   git subtree push --prefix backend heroku master

   # Or force push if needed:
   git push heroku `git subtree split --prefix backend master`:master --force
   ```

3. **Verify deployment**:
   ```bash
   heroku logs --tail -a hackthetrack-api
   curl https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api/health
   ```

### Frontend Deployment (Vercel)

**Automatic deployment** on push to master branch. No manual steps needed!

1. **Environment variable** (set in Vercel dashboard):
   - `VITE_API_URL=https://hackthetrack-api-ae28ad6f804d.herokuapp.com/api`

2. **Manual deployment** (if needed):
   ```bash
   cd frontend
   npm run build
   vercel deploy
   ```

### Data Updates

To update driver/track data:
1. Edit JSON files in `backend/data/`
2. Commit and push to GitHub
3. Deploy to Heroku (restarts and loads new data automatically)
4. No frontend changes needed - data flows through API

---

## 🔑 Key Technologies

### Backend
- **FastAPI**: Modern Python API framework
- **Anthropic SDK**: Claude 3.5 Sonnet integration
- **Pandas**: Data manipulation and analysis
- **Pydantic v2**: Data validation and settings
- **Custom error handling**: Structured logging with sanitized responses

### Frontend
- **React 19**: UI framework
- **React Router v7**: Client-side routing
- **Recharts**: Data visualization
- **Vite**: Build tool and dev server

### API Endpoints

#### Efficient Endpoints (Recommended for Skills Page)
```
GET /api/factors/{factor}/stats
```
Returns aggregated factor statistics (200 bytes):
- `top_3_average`: Average of top 3 drivers
- `league_average`: Average across all drivers
- `min`, `max`, `count`: Basic statistics

**Use this instead of loading all drivers** for statistics!

#### Standard Endpoints
```
GET /api/health                # Health check + data counts
GET /api/drivers               # All drivers (40KB)
GET /api/drivers/{number}      # Single driver (2KB)
GET /api/tracks                # All tracks
GET /api/drivers/{num}/season  # Season stats
GET /api/drivers/{num}/results # Race results
GET /api/predict               # Circuit fit prediction
GET /api/chat                  # AI strategy chat
```

---

## 📈 The 4-Factor Model

The platform is built on a validated statistical model with:
- **R² = 0.895** (explains 89.5% of race finishes)
- **MAE = 1.78 positions**
- **291 driver-race observations** across 12 races

### The 4 Factors (by importance):

1. **Raw Speed (50%)** - Qualifying pace, best lap times
2. **Consistency (31%)** - Lap-to-lap variation, sector consistency
3. **Racecraft (16%)** - Overtaking ability, position changes
4. **Tire Management (10%)** - Late-race pace preservation

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- Inspired by **PFF.com** (analytics presentation)
- Inspired by **DataGolf.com** (statistical modeling)
- Inspired by **VRS.racing** (telemetry comparison)
- Powered by **Anthropic Claude** (AI strategy coaching)
- Data from **Toyota GR86 Cup** racing series

---

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Email: support@example.com

---

**Built with ❤️ for grassroots motorsports**
