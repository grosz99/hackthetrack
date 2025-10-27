# Circuit Fit Analysis - Project Overview

## 🎯 Vision
Build a motorsports analytics product inspired by DataGolf's Course Fit Tool, adapted for racing circuits. Instead of telling drivers "your tire management score is 0.65," provide actionable feedback like:

> **"You're applying throttle 18% more aggressively than winners in Turn 3, costing 0.12 seconds per lap. Recommendation: Wait 2 meters past apex before throttle application."**

## 🏁 Product Concept
**Circuit Fit Analysis** shows how well a driver's skills match specific race tracks, providing:
- Corner-by-corner diagnostic breakdowns
- Comparison to winners and field averages
- Specific, actionable practice recommendations
- Statistical validation of feature discrimination

## 📊 Available Data (GR Cup Racing - "Hack the Track")
- Lap timing data
- Telemetry: speed, throttle, brake pressure, gear
- Section times (corner-by-corner)
- Race results
- Weather data
- **Note:** Qualifying data needs separate scraping from usac.alkamelna.com

## 🎓 Core Philosophy: Actionable > Analytical

### ❌ Bad (Analytical Theater)
- "Your tire management: 0.65/1.00"
- "Qualifying pace: 72nd percentile"
- "Technical precision: Above average"

### ✅ Good (Actionable Diagnostics)
- "Lap 8-12: Brake pressure drops 15% vs Lap 3. Earlier degradation than top 3. Try reducing initial brake force by 8%."
- "Turn 7: You apex 1.2m early, costing 0.09s. Move turn-in point 3m later."
- "Sector 2: Throttle application 0.3s earlier than winners but exit speed 4mph slower. You're getting wheelspin - delay throttle by 0.2s."

## 🏗️ System Architecture

### Phase 1: Statistical Validation
**Validate which features actually discriminate performance**
- Test features against finishing position
- Identify which metrics separate top-3, mid-pack, back-of-field
- Drop features that don't provide signal
- **Output:** Validated feature set with statistical significance

### Phase 2: Feature Engineering
**Extract meaningful metrics from raw telemetry**
- Corner-specific metrics (apex speed, braking points, throttle application)
- Consistency metrics (lap-to-lap variation)
- Tire degradation indicators
- Racecraft metrics (overtake success, defensive positions)

### Phase 3: Diagnostic Engine
**Generate specific, actionable feedback**
- Compare driver to field leaders
- Identify specific weaknesses with precision
- Generate practice recommendations
- Prioritize by time gain potential

### Phase 4: User Interface
**Present insights clearly and compellingly**
- Circuit overview with color-coded corner performance
- Detailed corner breakdowns
- Practice priority list
- Historical performance trends

## 📁 Documentation Structure

```
00_PROJECT_OVERVIEW.md          ← You are here
01_DATA_STRUCTURES.md           ← Input data formats and schemas
02_FEATURE_ENGINEERING.md       ← How to extract metrics from telemetry
03_STATISTICAL_VALIDATION.md   ← How to validate feature discrimination
04_DIAGNOSTIC_ENGINE.md         ← How to generate actionable feedback
05_IMPLEMENTATION_GUIDE.md      ← Step-by-step build instructions
06_CIRCUIT_KNOWLEDGE.md         ← Track-specific racing expertise
```

## 🎯 Success Criteria

A driver should be able to:
1. **Understand** exactly where they're losing time
2. **Know** specifically what to change
3. **Practice** with concrete technique adjustments
4. **Measure** improvement on subsequent track visits

## 🚀 Quick Start for Claude Code

1. Read all documentation files in order
2. Start with `01_DATA_STRUCTURES.md` to understand available data
3. Build statistical validation pipeline from `03_STATISTICAL_VALIDATION.md`
4. Implement feature engineering from `02_FEATURE_ENGINEERING.md`
5. Build diagnostic engine from `04_DIAGNOSTIC_ENGINE.md`
6. Follow `05_IMPLEMENTATION_GUIDE.md` for full system

## 📝 Key Design Principles

1. **Evidence-Based**: Only use features proven to discriminate performance
2. **Actionable First**: Every metric must answer "what should I do differently?"
3. **Precision Over Aggregation**: Corner 3 feedback > overall track score
4. **Comparative Context**: Always show driver vs winners vs field average
5. **Prioritized Recommendations**: Sort by time gain potential
6. **Data-Driven Validation**: Test everything against actual race results

## 🏎️ Technical Stack Recommendations

- **Data Processing**: Python (pandas, numpy)
- **Statistical Analysis**: scipy, statsmodels
- **Visualization**: plotly, matplotlib
- **Storage**: SQLite or PostgreSQL for lap/telemetry data
- **Frontend**: Streamlit for MVP, React for production
- **API**: FastAPI for backend services

## 🎪 Demo Data
GR Cup racing data from Toyota "Hack the Track" hackathon
- Multiple tracks: Barber, Sonoma, Road America, Sebring, VIR
- Multiple drivers per race
- Full telemetry and timing data available

## 📚 Next Steps
1. **Read**: `01_DATA_STRUCTURES.md` to understand data format
2. **Validate**: Run statistical tests from `03_STATISTICAL_VALIDATION.md`
3. **Build**: Feature pipeline from `02_FEATURE_ENGINEERING.md`
4. **Test**: Diagnostic outputs from `04_DIAGNOSTIC_ENGINE.md`
5. **Deploy**: Follow `05_IMPLEMENTATION_GUIDE.md`

---

**Remember**: The goal isn't to build fancy analytics. The goal is to make drivers faster. Every feature, every chart, every number must answer: "What should I do differently?"
