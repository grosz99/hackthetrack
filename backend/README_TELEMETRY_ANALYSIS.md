# Telemetry Turn-by-Turn Analysis - Quick Start Guide

## Overview

Automatic corner detection and analysis system that processes high-frequency telemetry data (20-40Hz) to generate driver coaching insights like "Brake 10 meters later into Turn 3."

**Status**: MVP Complete ✅
**Processing Speed**: 2.5 seconds per race (122MB, 1M rows)
**Output**: JSON with corner metrics for API integration

---

## Quick Start

### 1. Process a Race

```python
from telemetry_corner_analysis import TelemetryProcessor

# Initialize
processor = TelemetryProcessor(
    data_dir="data/telemetry/processed"
)

# Process Barber Race 1
results = processor.process_race(
    track_name="barber",
    race_num=1,
    vehicle_numbers=[7, 13],  # Optional: specific drivers
    best_lap_only=True
)

# Save results
processor.save_results(
    results,
    "output/barber_r1_analysis.json"
)
```

### 2. Compare Two Drivers

```python
from telemetry_corner_analysis import compare_drivers, print_comparison_report

# Compare drivers on specific corner
comparison = compare_drivers(
    results,
    driver_a=7,
    driver_b=13,
    corner_num=1
)

# Print coaching insights
print_comparison_report(comparison)
```

### 3. Run Sample Analysis

```bash
# Process Barber Race 1, compare drivers 7 vs 13
python backend/telemetry_corner_analysis.py
```

**Output Files**:
- `backend/data/corner_analysis_barber_r1.json` - Full analysis
- `backend/data/corner_comparison_example.json` - Comparison example

---

## Key Files

| File | Purpose | Size |
|------|---------|------|
| `telemetry_corner_analysis.py` | Main processing script | 503 lines |
| `CORNER_DETECTION_METHODOLOGY.md` | Detailed algorithm docs | 4,847 words |
| `TELEMETRY_ANALYSIS_SUMMARY.md` | Complete implementation summary | 3,200 words |
| `data/track_layouts.json` | Track corner definitions | 15 KB |

---

## Corner Metrics Extracted

1. **Braking Point** (meters) - Where driver brakes before corner
2. **Entry Speed** (km/h) - Speed at turn-in point
3. **Apex Speed** (km/h) - Minimum speed in corner
4. **Exit Speed** (km/h) - Speed at corner exit
5. **Corner Time** (seconds) - Time from entry to exit
6. **Lateral G Max** (g-force) - Peak cornering force
7. **Steering Smoothness** (std dev) - Input consistency
8. **Brake Pressure Max** (bar) - Peak braking force
9. **Throttle Application Point** (meters) - Where throttle applied

---

## Example Output

### Coaching Insight
```
Turn 1 Analysis: Driver 7 vs Driver 13

Driver 13 is 0.3s faster through Turn 1

Key Differences:
✓ Brakes 15 meters LATER (125m vs 110m) → Gains 0.12s
✓ Carries 3.2 km/h MORE entry speed (188.4 vs 185.2) → Gains 0.08s
✓ Apex speed 1.8 km/h HIGHER (95.1 vs 93.3) → Gains 0.06s
✓ Exit speed 4.1 km/h HIGHER (147.3 vs 143.2) → Gains 0.04s

Recommendation for Driver 7:
1. Brake 15 meters later into Turn 1
2. Trust the grip - carry more entry speed
3. Get back to throttle 8 meters earlier
```

---

## Performance Benchmarks

| Metric | Value |
|--------|-------|
| Single race (122MB, 1M rows) | 2.5 seconds |
| All races (1.6GB, 11M rows) | ~4-5 minutes |
| Output JSON size | ~1.5 MB (300 KB compressed) |
| Memory usage (peak) | 1.2 GB RAM |

---

## Track Support

| Track | Length | Corners | Status |
|-------|--------|---------|--------|
| Barber Motorsports Park | 3.85 km | 17 | ✅ Tested |
| Circuit of The Americas | 5.51 km | 20 | ✅ Mapped |
| Road America | 6.52 km | 14 | ✅ Mapped |
| Sonoma Raceway | 4.00 km | 12 | ✅ Mapped |
| Virginia Int'l Raceway | 5.26 km | 18 | ✅ Mapped |

---

## Next Steps

### Phase 1 (Current) - MVP ✅
- [x] Auto-detection algorithm
- [x] Corner metric extraction
- [x] Driver comparison
- [x] JSON output format

### Phase 2 (Next) - Refinement
- [ ] Tune corner splitting for chicanes
- [ ] Integrate manual track layouts
- [ ] Build FastAPI endpoints
- [ ] Frontend dashboard integration

### Phase 3 (Future) - Advanced
- [ ] GPS validation
- [ ] Historical trend analysis
- [ ] Machine learning optimization
- [ ] Real-time processing

---

## Known Limitations

1. **Corner Merging**: Chicanes sometimes detected as single corner
   - **Mitigation**: Tune merge gap or use manual definitions

2. **Missing Data**: Some samples have NaN values
   - **Mitigation**: Handle with fallback logic

3. **Lap Boundaries**: Corners crossing start/finish line
   - **Mitigation**: Wrap distance calculations

---

## API Integration (Future)

```python
# FastAPI endpoint example
@app.get("/api/corner-analysis/{track}/{race}/{driver}")
async def get_corner_analysis(track: str, race: int, driver: int):
    # Load pre-computed results
    results = load_analysis_results(track, race)
    driver_data = results['drivers'].get(str(driver))
    return driver_data

@app.get("/api/corner-comparison/{track}/{race}/{driver_a}/{driver_b}/{corner}")
async def get_corner_comparison(
    track: str,
    race: int,
    driver_a: int,
    driver_b: int,
    corner: int
):
    results = load_analysis_results(track, race)
    comparison = compare_drivers(results, driver_a, driver_b, corner)
    return comparison
```

---

## Troubleshooting

### Error: File not found
```python
# Check data directory path
processor = TelemetryProcessor(
    data_dir="/full/path/to/data/telemetry/processed"
)
```

### Warning: Corner detection failed
- Increase minimum corner duration threshold
- Reduce steering angle threshold
- Check for missing telemetry data

### Memory issues with large files
```python
# Process in chunks (future enhancement)
# Current: loads full file into memory
```

---

## Support

**Documentation**:
1. `CORNER_DETECTION_METHODOLOGY.md` - Algorithm details
2. `TELEMETRY_ANALYSIS_SUMMARY.md` - Complete implementation guide
3. Code comments in `telemetry_corner_analysis.py`

**Test Data**:
- `data/telemetry/processed/barber_r1_wide.csv` (122 MB)
- Sample output in `backend/data/`

**Questions?** Review the methodology document or test on sample data.

---

**Last Updated**: 2025-11-10
**Version**: 1.0
**Status**: Ready for Integration Testing
