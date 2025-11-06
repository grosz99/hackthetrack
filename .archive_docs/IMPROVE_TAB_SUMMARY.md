# Improve Tab - AI Telemetry Coaching Lab

## 🏁 Overview

The Improve tab has been completely transformed into an **AI-powered telemetry coaching interface** that provides race engineer-style analysis and actionable recommendations. This feature is designed to win the Toyota GR Cup hackathon by delivering professional-grade coaching insights that help drivers improve lap times.

## ✨ Key Features

### 1. Smart Comparison System
- **Quick Pick Buttons**: "Winner" and "Next Tier" for instant comparison selection
- **Progressive Disclosure**: Advanced dropdown hidden until needed
- **Smart Defaults**: Auto-selects first available comparison driver

### 2. Hero Metric Display
- **Prominent Time Gain**: Large red gradient card showing potential lap time improvement
- **Visual Hierarchy**: Hero metric is 2x size of supporting metrics
- **Supporting Metrics**: Lap delta, track info, and focus corners count

### 3. Corner-by-Corner Analysis
- **Data Table**: 6-column breakdown showing:
  - Corner number and name
  - Driver apex speed vs reference
  - Speed delta
  - Time loss per corner
  - Focus area (Brake Point / Apex Speed / Throttle Application)
- **Visual Highlighting**: Red background for corners with >0.05s time loss
- **Hover Effects**: Interactive rows with transitions

### 4. AI Race Engineer Coaching
- **Claude Sonnet 4.5**: Deep analysis using latest model
- **Structured Format**: 3-5 priority areas with:
  - What the data shows (specific telemetry observations)
  - What to do (actionable coaching)
  - Why it matters (physics/technique explanation)
- **Markdown Rendering**: Professional formatting with ReactMarkdown

### 5. Telemetry Pattern Insights
- **Overall Analysis**: Braking, throttle, speed, and steering patterns
- **Comparison Stats**: Driver vs reference across all channels
- **Grid Layout**: Clean card-based presentation

## 🎨 Design System Compliance

✅ Dark background (#0a0a0a)
✅ White cards with 4px red borders (#e74c3c)
✅ Bold typography (Inter font family)
✅ Racing-themed (uppercase labels, high contrast)
✅ Smooth transitions and hover effects
✅ Responsive layout (desktop/tablet/mobile)

## 🔧 Technical Implementation

### Backend (`/backend`)

**New Files:**
- `app/services/ai_telemetry_coach.py` - AI coaching service with Claude integration
- Added to `app/api/routes.py`:
  - `POST /api/telemetry/coaching` - Main coaching endpoint
  - Helper functions for telemetry analysis and corner detection

**Models (`/backend/models/models.py`):**
- `TelemetryCoachingRequest` - Request model
- `TelemetryCoachingResponse` - Response with coaching + analysis
- `CornerAnalysis` - Per-corner breakdown model
- `TelemetryPoint` - Individual telemetry data point

### Frontend (`/frontend`)

**Updated Files:**
- `src/pages/Improve/Improve.jsx` - Complete rewrite
  - Smart comparison selector with quick picks
  - Hero metric layout
  - Corner analysis table
  - AI coaching display

- `src/pages/Improve/Improve.css` - Complete redesign
  - Hero metric styling (gradient background)
  - Quick pick buttons
  - Progressive disclosure patterns
  - Responsive breakpoints

**Dependencies:**
- Added `react-markdown` for coaching text rendering

## 📊 Data Flow

```
1. User selects: Track → Race → Comparison Driver
2. Clicks "Analyze Telemetry"
3. Frontend → POST /api/telemetry/coaching
4. Backend loads telemetry CSVs from data/telemetry/
5. Analyzes:
   - Overall telemetry patterns
   - Corner-by-corner performance (using scipy peak detection)
   - Calculates time losses
6. Generates AI coaching via Claude API
7. Returns structured response
8. Frontend displays:
   - Hero metric (potential time gain)
   - Corner table
   - AI coaching markdown
   - Telemetry insights
```

## 🎯 UX Improvements Implemented

Based on sports-recruiting-ux-designer consultation:

### ✅ Priority #1: Progressive Disclosure
- Quick pick buttons for 80% use case (Winner/Next Tier)
- Advanced dropdown hidden in `<details>` element
- Reduces cognitive load on first use

### ✅ Priority #2: Hero Metric Prominence
- Potential Time Gain is 2x size in gradient red card
- Answers "Is this analysis worth my time?" immediately
- Supporting metrics provide context without overwhelming

### ✅ Priority #3: Smart Comparison Defaults
- Visual buttons with icons (🏆 Winner, 🎯 Next Tier)
- Tooltips explain each option
- Active state shows current selection

### ✅ Priority #4: Visual Hierarchy
- Large numbers for key metrics
- Color coding (red = loss, green = gain)
- Focus corners highlighted in table

### ✅ Priority #5: Coaching Actionability
- AI provides specific numbers from telemetry
- Clear "What to do" sections
- Physics explanations for understanding

## 🚀 Usage Instructions

### For Drivers:

1. Navigate to **Improve** tab from dashboard
2. Select your **track** and **race number**
3. Choose comparison:
   - Click **🏆 Winner** for race winner comparison
   - Click **🎯 Next Tier** for incremental improvement
   - Or expand "Select specific driver" for custom choice
4. Click **Analyze Telemetry**
5. Review:
   - **Potential Time Gain** (hero metric)
   - **Corner-by-Corner** table (focus on red rows)
   - **AI Coaching** (priority #1 is most important)
   - **Telemetry Patterns** for overall insights

### For Developers:

**Start Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

**Test Coaching Endpoint:**
```bash
curl -X POST http://localhost:8000/api/telemetry/coaching \
  -H "Content-Type: application/json" \
  -d '{
    "driver_number": 7,
    "reference_driver_number": 3,
    "track_id": "barber",
    "race_num": 1
  }'
```

## 📈 Success Metrics

### For Hackathon Judging:

✅ **Innovation**: AI-powered coaching vs static data displays
✅ **User Value**: Actionable insights drivers can immediately use
✅ **Technical Execution**: Full-stack integration (React + FastAPI + Claude)
✅ **Design Quality**: Racing-themed, professional UI matching existing dashboard
✅ **Data Utilization**: Leverages telemetry CSVs + AI for insights

### Driver Impact:

- **Time Savings**: Identifies top 3-5 opportunities vs manual analysis
- **Clarity**: Specific numbers (brake points, apex speeds) vs vague advice
- **Prioritization**: Focuses on biggest gains first
- **Learning**: Explains physics/technique behind recommendations

## 🔮 Future Enhancements

Based on UX consultant recommendations (not implemented yet):

1. **Session Plan Generator**: Convert coaching into lap-by-lap practice plan
2. **Multi-Driver Comparison**: Compare against 2-3 drivers simultaneously
3. **Priority Focus Mode**: Show only top priority, hide rest until completed
4. **Mobile Timeline View**: Visual corner timeline instead of table on mobile
5. **Share/Export**: Print coaching sheet, share with coach via email
6. **Historical Tracking**: Track improvement over time as driver practices recommendations

## 🏆 Hackathon Demo Points

**Key Talking Points:**

1. **"Professional race engineer in your pocket"**
   - Show how AI analyzes 20+ corners and provides 3-5 priority coaching points
   - Demonstrate specific numbers (e.g., "Brake 30m later at Turn 5")

2. **"Smart comparison system"**
   - Show quick pick buttons (Winner vs Next Tier)
   - Explain how this guides drivers to realistic targets

3. **"Hero metric prominence"**
   - Highlight the large "Potential Time Gain" card
   - Show how this immediately answers "Should I focus here?"

4. **"Data-driven insights"**
   - Walk through corner-by-corner table
   - Show how red highlighting draws attention to biggest opportunities

5. **"Full-stack AI integration"**
   - Backend loads real telemetry CSVs
   - Claude analyzes and generates coaching
   - Frontend displays with racing-themed UI

## 📝 Environment Setup

**Required Environment Variables:**
```bash
# backend/.env
ANTHROPIC_API_KEY=your_key_here
```

**Data Requirements:**
- Telemetry files in `data/telemetry/` (e.g., `barber_r1_wide.csv`)
- Must include columns: `vehicle_number`, `lap`, `speed`, `pbrake_f`, `aps`, `Steering_Angle`

## 🐛 Known Issues / Limitations

1. **Corner Detection**: Currently uses scipy peak detection (speed minima) as proxy
   - Future: Use actual corner GPS coordinates for accuracy

2. **Time Delta Calculation**: Simplified estimate (1 km/h ≈ 0.01s)
   - Future: Use actual lap time data for precise calculations

3. **Telemetry Alignment**: Assumes laps are similar length
   - Future: Align by distance or GPS coordinates

4. **Loading Time**: AI coaching generation takes 5-15 seconds
   - Already using Sonnet (fast model)
   - Could add progress indicator

## 🎓 Learning Resources

- **AI Coaching Prompt**: See `backend/app/services/ai_telemetry_coach.py` line 15
- **Corner Analysis**: See `backend/app/api/routes.py` line 1030
- **Hero Metric Pattern**: See UX consultant response (progressive disclosure)
- **Racing UX**: Sports-recruiting-ux-designer agent recommendations

---

**Built for**: Toyota GR Cup Hack the Track Hackathon
**Status**: ✅ Complete and ready for demo
**Last Updated**: 2025-11-03
