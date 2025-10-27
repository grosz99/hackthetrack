# Analysis Priorities - HackTheTrack Project

## Primary Goal
**Discover the 6 key driver skills through data-driven EDA, NOT assumptions.**

---

## Priority Order

### 1. EXPLORATORY DATA ANALYSIS (HIGHEST PRIORITY)
**File: `EDA_DISCOVERY_GUIDE.md`**

This is your starting point. DO NOT skip to feature engineering or implementation.

**Why First:**
- We don't know what the 6 skills are yet
- Need to let the data tell us which skills discriminate winners from losers
- All subsequent work depends on discovering these skills

**Key Deliverables:**
- [ ] Identify which corners/sections discriminate between performance groups
- [ ] Cluster corners into natural skill groupings
- [ ] Test consistency, tire degradation, racecraft metrics
- [ ] Rank ALL potential skills by discrimination power
- [ ] Select final 6 skills based on statistical validation
- [ ] Document discovered skills in `data/analysis_outputs/discovered_skills.json`

**Output Needed:**
```json
{
  "skill_1": {
    "name": "TBD from data",
    "description": "TBD from data",
    "p_value": "TBD",
    "effect_size": "TBD",
    "corners_or_metric": "TBD"
  }
  // ... 5 more skills
}
```

---

### 2. DATA UNDERSTANDING
**Folder: `Analysis_Setup/`**

Review these AFTER starting EDA, as reference material.

**Priority Files:**
1. `00_PROJECT_OVERVIEW.md` - Quick context
2. `01_DATA_STRUCTURES.md` - What data we have
3. `06_CIRCUIT_KNOWLEDGE.md` - Track characteristics

**Why Second:**
- Provides context for EDA findings
- Helps interpret corner groupings
- Reference material, not implementation guide

---

### 3. FEATURE ENGINEERING (After EDA Complete)
**File: `Analysis_Setup/02_FEATURE_ENGINEERING.md`**

DO NOT START until you have discovered skills from EDA.

**Why Third:**
- Features should be based on discovered skills
- No point building features before knowing what matters
- Engineering follows discovery

---

### 4. STATISTICAL VALIDATION
**File: `Analysis_Setup/03_STATISTICAL_VALIDATION.md`**

Validate that your discovered skills actually work.

**Why Fourth:**
- Verify skills discriminate performance
- Check correlations between skills
- Ensure statistical rigor

---

### 5. IMPLEMENTATION
**Files:**
- `Analysis_Setup/04_DIAGNOSTIC_ENGINE.md`
- `Analysis_Setup/05_IMPLEMENTATION_GUIDE.md`

Build the actual system once you know what to build.

**Why Last:**
- Can't build until you know the 6 skills
- Implementation follows validated discovery
- Code the solution, don't assume it

---

## Current Status

### Completed:
- [x] Data restructuring (organized by file type)
- [x] Data pushed to GitHub (grosz99/hackthetrack)
- [x] Folder structure created:
  - raw_telemetry/
  - processed_telemetry/
  - lap_timing/
  - race_results/
  - analysis_outputs/

### Next Immediate Step:
**START EDA using `EDA_DISCOVERY_GUIDE.md`**

1. Load data from the new file structure:
   ```python
   # Use the reorganized data paths
   race_results = pd.read_csv('data/race_results/provisional_results/barber_r1_provisional_results.csv')
   lap_times = pd.read_csv('data/lap_timing/barber_r1_lap_time.csv')
   best_laps = pd.read_csv('data/race_results/best_10_laps/barber_r1_best_10_laps.csv')
   analysis = pd.read_csv('data/race_results/analysis_endurance/barber_r1_analysis_endurance.csv')
   ```

2. Follow the EDA guide step-by-step
3. Document findings as you go
4. Output `discovered_skills.json` when complete

---

## What NOT to Do

- Don't assume you know the 6 skills already
- Don't start building features before EDA
- Don't skip statistical validation
- Don't jump to implementation
- Don't use the Analysis_Setup files as implementation guides yet

---

## Success Criteria

You'll know you're ready to move on when:
1. You have 6 statistically validated skills (p < 0.05, |d| > 0.5)
2. Skills have low correlation (not measuring the same thing)
3. Skills are actionable (driver can improve them)
4. Skills are documented in JSON format
5. You have visualizations showing discrimination power

---

## Questions to Answer Through EDA

1. Which specific corners separate fast from slow drivers?
2. Do corners cluster into natural skill groups?
3. Does consistency discriminate performance?
4. Does tire management discriminate performance?
5. Does racecraft (positions gained) discriminate performance?
6. What are the 6 most discriminating, independent skills?

**Let the data answer these questions. Don't assume.**

---

## File Organization

```
.claude/
├── ANALYSIS_PRIORITIES.md          ← YOU ARE HERE (start here)
├── EDA_DISCOVERY_GUIDE.md           ← STEP 1: Do this first
├── Analysis_Setup/
│   ├── 00_PROJECT_OVERVIEW.md       ← Reference material
│   ├── 01_DATA_STRUCTURES.md        ← Reference material
│   ├── 02_FEATURE_ENGINEERING.md    ← STEP 3: After EDA
│   ├── 03_STATISTICAL_VALIDATION.md ← STEP 4: Validate skills
│   ├── 04_DIAGNOSTIC_ENGINE.md      ← STEP 5: Build system
│   ├── 05_IMPLEMENTATION_GUIDE.md   ← STEP 5: Build system
│   └── 06_CIRCUIT_KNOWLEDGE.md      ← Reference material
├── AGENT_1_DATA_SCIENCE.md          ← Legacy agent docs
├── AGENT_2_FRONTEND.md              ← Legacy agent docs
└── AGENT_3_COACHING.md              ← Legacy agent docs
```

---

## Quick Start Command

```bash
# Navigate to project
cd c:/Users/PC/Documents/gazoo_raicing_files

# Open Jupyter or Python
jupyter notebook

# Start with EDA
# Follow: .claude/EDA_DISCOVERY_GUIDE.md
```

---

**Remember: Discovery before engineering. Let the data tell you the answer.**
