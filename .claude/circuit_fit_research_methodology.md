# Circuit Fit Analysis: Research Methodology
## Discovering Driver Skill Dimensions in GR Cup Spec Racing

**Project Goal:** Build a validated model that identifies core driver skills, creates track-specific demand profiles, and provides actionable preparation insights for amateur racers.

**Inspiration:** RepTrak Reputation Model (23 observable attributes → 7 latent factors)

---

## PHASE 1: EXPLORATORY FACTOR ANALYSIS (Discovering Skills)

### The Problem We're Solving
**Unlike F1 research**, where constructor explains 88% of variance, **spec racing is 90% driver skill** - but WHAT skills? Nobody has validated this scientifically.

### Your Hypothesis
You believe there are **5 core skill dimensions**:
1. **SPEED** - Raw pace capability
2. **BRAKING** - Deceleration technique and control
3. **CORNERING** - Turning technique and momentum management  
4. **TIRE MANAGEMENT** - Pace consistency over stint length
5. **RACECRAFT** - Overtaking and positioning in traffic

### Research Question
**Do these 5 dimensions actually exist in the data, or is performance explained by different/fewer factors?**

---

## CYCLING RESEARCH PARALLEL - WHY THIS METHODOLOGY WORKS

### **Power Duration Curves → Driver Skill Profiles**

**Cycling's Approach:**
- Sprint power (5s) vs Anaerobic (1min) vs VO2max (5min) vs FTP (20min)
- Creates "phenotypes": Sprinter, Time Trialist, Climber, All-Rounder
- **Problem:** These are ASSUMED categories, never validated with factor analysis

**Your Approach (Better):**
- Speed vs Braking vs Cornering vs Tire Management vs Racecraft
- Use **Exploratory Factor Analysis** to discover if these dimensions exist
- Validate against race results to prove they predict winning

### **Terrain-Specific Demands**

**Cycling:** Flat courses favor sprinters, mountains favor climbers, time trials favor sustained power
**Racing:** High-speed tracks (COTA) favor late-braking, technical tracks (Barber) favor momentum

### **The "Race-Winning Effort" Problem**

**CRITICAL INSIGHT from Cycling Research:**
> "MMP analysis may be missing the very efforts that it is trying to identify... the power output that riders produce at key moments in the race is predictive of performance"

**Application to Racing:**
- Don't just measure fastest lap (like MMP)
- Measure performance in **decisive race moments**:
  - Late-race pace (laps 15-20 vs laps 1-5)
  - Restart performance (first lap after safety car)
  - Passing zone performance (speed/braking in high-overtaking corners)
  - Traffic performance (lap time when within 1s of another car)

---

## STEP 1: ENGINEER OBSERVABLE VARIABLES (20-25 metrics)

Build telemetry-based metrics that might load onto skill factors. Group by your hypothesized dimensions:

### **SPEED Observables (5 variables)**
All from qualifying/race data, NOT telemetry:

**CYCLING INSIGHT:** Peak performance ≠ race-winning performance. Measure speed at *critical moments* not just best lap.

1. **Qualifying Pace Index** = (Driver's Q time - Track record) / Track record [Peak performance]
2. **Late-Race Pace** = Average lap time in final 25% of race vs race winner [Race-winning moment]
3. **Restart Performance** = Average first lap after safety car vs field average [Critical moment]
4. **Clean Air Pace** = Average lap time when >3 seconds clear of traffic [Context-controlled]
5. **Straight Speed Percentile** = Ranking of max speed on longest straight [Raw speed capability]

### **BRAKING Observables (5 variables)** 
All from telemetry - isolates braking skill:

6. **Peak Brake Pressure** = Average max brake pressure across all major braking zones
7. **Braking Point Consistency** = StdDev of brake application point (distance from corner) on clean laps
8. **Brake Modulation Smoothness** = Average rate of change in brake pressure (lower = smoother)
9. **Brake Duration Efficiency** = Time on brakes / Speed reduction achieved (lower = more efficient)
10. **Trail Braking Skill** = % of corners where brake release occurs after turn-in point

### **CORNERING Observables (5 variables)**
From telemetry - pure cornering ability:

11. **Minimum Corner Speed** = Average min speed in corners (higher = better momentum)
12. **Lateral G Consistency** = StdDev of peak lateral G across repeated corners
13. **Steering Smoothness** = Average rate of steering input change (lower = smoother)
14. **Apex Precision** = Average distance from optimal racing line at apex
15. **Corner Exit Quality** = Time delta from apex to full throttle vs fastest driver

### **TIRE MANAGEMENT Observables (4 variables)**
From lap times - consistency analysis:

16. **Lap Time Degradation** = Slope of lap time vs lap number over stint (on clean laps)
17. **Consistency Under Pressure** = Lap time StdDev when within 1s of another car
18. **Long Run Pace** = Average lap time in laps 5-15 vs laps 1-4
19. **Sector Time Variance** = StdDev of sector times on clean laps (excludes traffic)

### **RACECRAFT Observables (3 variables)**
From race results + telemetry:

20. **Overtaking Success Rate** = (Passes completed) / (Time spent <0.25s behind another car)
21. **Defending Skill** = % of defensive situations where position maintained for >2 laps
22. **Traffic Navigation** = Lap time delta in traffic vs clean air (lower = better)

**CRITICAL:** These are starting hypotheses. Factor analysis will reveal which variables actually cluster together.

---

## STEP 2: RUN EXPLORATORY FACTOR ANALYSIS

### Data Structure Required
- **Rows:** Each driver-track combination (e.g., Driver A at Barber, Driver A at COTA)
- **Columns:** Your 22 observable variables + finishing position
- **Sample Size:** Need ~10 observations per variable = 220+ driver-track combos minimum

### EFA Process

**Step 2.1: Check Data Suitability**
```python
# Test if your variables are correlated enough for factor analysis
from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
from factor_analyzer.factor_analyzer import calculate_kmo

# Bartlett's test: p < 0.05 means variables are correlated
chi_square_value, p_value = calculate_bartlett_sphericity(data)

# KMO > 0.6 is acceptable, >0.8 is great
kmo_all, kmo_model = calculate_kmo(data)
```

**Step 2.2: Determine Number of Factors**
```python
from factor_analyzer import FactorAnalyzer

# Create scree plot to see how many factors to extract
fa = FactorAnalyzer(rotation=None, n_factors=22)
fa.fit(data)

# Plot eigenvalues - look for "elbow" 
import matplotlib.pyplot as plt
ev = fa.get_eigenvalues()[0]
plt.plot(range(1, len(ev)+1), ev)
plt.xlabel('Factor Number')
plt.ylabel('Eigenvalue')
plt.title('Scree Plot')
```

**YOU MIGHT DISCOVER:** Only 4 factors with eigenvalue >1, not 5! Or maybe 6! Let the data tell you.

**Step 2.3: Extract Factors with Rotation**
```python
# Use oblique rotation - allows factors to correlate
fa = FactorAnalyzer(n_factors=5, rotation='oblimin')  # Start with your hypothesis
fa.fit(data)

# Get factor loadings - which variables load on which factors?
loadings = fa.loadings_
```

**Step 2.4: Interpret the Factors**
- Look at which variables load strongly (>0.5) on each factor
- **Name the factors based on what loaded**, not your hypothesis
- Example: If "Braking Point Consistency" and "Steering Smoothness" load together → might be "Precision" not "Braking"

---

## STEP 3: VALIDATE AGAINST RACE RESULTS

### Test: Do These Factors Actually Predict Winning?

```python
from sklearn.linear_model import LinearRegression
from scipy import stats

# Get factor scores for each driver-track combo
factor_scores = fa.transform(data)

# Does Factor 1 correlate with finishing position?
for i in range(num_factors):
    correlation, p_value = stats.pearsonr(factor_scores[:, i], finishing_positions)
    print(f"Factor {i+1} correlation with finish: {correlation:.3f} (p={p_value:.4f})")
```

**SUCCESS CRITERIA:**
- At least 3 factors should significantly correlate (p < 0.05) with finishing position
- Combined factors should explain >60% of variance in results (R² > 0.6)

---

## STEP 4: CREATE TRACK DEMAND PROFILES

### Method: Track-Specific Factor Importance

For each track, calculate which factors matter most for success:

```python
import pandas as pd

# For each track separately:
for track in tracks:
    track_data = data[data['track'] == track]
    
    # Run regression: Finishing Position ~ Factor1 + Factor2 + ... + Factor5
    X = factor_scores[data['track'] == track]
    y = finishing_positions[data['track'] == track]
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Coefficients show which factors matter most at this track
    track_profiles[track] = {
        'Factor1_weight': abs(model.coef_[0]),
        'Factor2_weight': abs(model.coef_[1]),
        # ... etc
    }
```

**OUTPUT:** Track demand profiles showing which skills predict success at each circuit

**Example:**
- **COTA (high-speed):** Speed=0.45, Braking=0.10, Cornering=0.25, Tire=0.15, Racecraft=0.05
- **Barber (technical):** Speed=0.15, Braking=0.35, Cornering=0.40, Tire=0.05, Racecraft=0.05

---

## STEP 5: DRIVER-TRACK FIT SCORING

### Calculate Individual Driver Skill Profiles

```python
# For each driver, get their factor scores averaged across all tracks
driver_profiles = {}
for driver in drivers:
    driver_data = factor_scores[data['driver'] == driver]
    driver_profiles[driver] = {
        'Factor1': np.mean(driver_data[:, 0]),
        'Factor2': np.mean(driver_data[:, 1]),
        # ... etc
    }
```

### Calculate Fit Score for Each Driver-Track Combination

```python
# For upcoming track:
track = "Barber"
track_demand = track_profiles[track]  # Which factors matter at Barber?

for driver in drivers:
    fit_score = 0
    insights = []
    
    for factor in factors:
        # How much does this track demand this skill?
        demand = track_demand[f'{factor}_weight']
        
        # How strong is this driver at this skill?
        ability = driver_profiles[driver][factor]
        
        # Contribution to fit
        fit_score += demand * ability
        
        # Actionable insight
        if demand > 0.3 and ability < 0:  # High demand, weak skill
            insights.append(f"Focus on {factor_name[factor]} - high track demand, opportunity area")
        elif demand < 0.2 and ability > 0.5:  # Low demand, strong skill
            insights.append(f"{factor_name[factor]} is your strength but less critical here")
```

**OUTPUT FOR USER:**
```
Driver: Justin Grosz
Track: Barber Motorsports Park
Fit Score: 0.72 (Good match)

Track Demands:
- Braking: 35% importance
- Cornering: 40% importance  
- Speed: 15% importance
- Tire Management: 5% importance
- Racecraft: 5% importance

Your Strengths:
✓ Cornering (90th percentile)
✓ Tire Management (85th percentile)

Focus Areas for Barber:
⚠ Braking - HIGH track demand (35%), you're 45th percentile
  → Practice late braking in T5 and T17
  → Work on brake modulation consistency

✓ Speed - Low track demand here, momentum matters more

Expected Result: Top-10 finish achievable with improved braking
```

---

## WHY THIS RESEARCH IS NOVEL & VALUABLE

### **What Makes This Different:**

**1. First Factor Analysis in Spec Racing**
- Motorsports research focuses on F1 (constructor dominates)
- Cycling research assumes skill categories without validation
- **You'll be first to use EFA to discover driver skill dimensions**

**2. RepTrak Methodology Applied to Sports**
- Proven framework from reputation research
- Observable variables → latent factors → predictive model
- Validated by correlation with business outcomes (your outcome = race results)

**3. Actionable Intelligence vs Academic Research**
- Most research: "Drivers differ in performance" (unhelpful)
- Your approach: "Focus 70% of practice on braking at this track" (actionable)

**4. Amateur Racing Focus**
- Pro racing has unlimited telemetry analysis resources
- **GR Cup drivers need tools they can actually use**
- Your system answers: "What should I work on this week?"

### **Academic Contribution:**

If you write this up properly, you could publish in:
- *Journal of Sports Sciences*
- *Sports Medicine*  
- *International Journal of Sports Performance Analysis*

**Novel findings:**
1. Validated skill dimensions in spec racing (never done)
2. Track-specific skill demands (racing version of terrain profiling)
3. Driver-track fit prediction model
4. Comparison to cycling power profiling methodology

### **Commercial Value:**

- **DataGolf for Racing** - subscription service for amateur racers
- **Team scouting tool** - "Which driver fits our track schedule?"
- **Training prioritization** - AI-powered practice recommendations
- **Track day preparation** - Weekend warrior version

---

## NEXT STEPS

1. **Validate you have enough data**
   - Need 220+ driver-track combinations minimum (10 per variable)
   - With 6 tracks × 20 drivers/track × 2-3 races = ~240-360 observations ✓

2. **Clean and structure your data**
   - One row per driver-track-race combination
   - Calculate all 22 observable variables
   - Add finishing position as outcome variable

3. **Run EFA to discover factors**
   - Test 3-7 factor solutions
   - Let the data tell you how many dimensions exist
   - Interpret factors based on variable loadings

4. **Validate against results**
   - Do factors correlate with finishing position?
   - R² > 0.6 means you've captured meaningful variance

5. **Build track demand profiles**
   - Run track-specific regressions
   - Identify which factors matter at each circuit

6. **Create driver fit tool**
   - Calculate driver skill profiles
   - Generate actionable recommendations

**Want me to build the Python implementation?**