# Circuit Fit Analytics - Database Implementation (SQLite)

## Why SQLite is Perfect for This Hackathon

1. **No server setup** - It's just a file
2. **Can commit to Git** - Judges can run immediately
3. **Pre-populated data** - Process once, use everywhere
4. **Fast queries** - Better than JSON parsing
5. **Real SQL** - Shows technical depth

---

## Option 1: SQLite with Pre-Processed Data (RECOMMENDED)

### Setup Script
```bash
# Install dependencies
npm install better-sqlite3
npm install --save-dev @types/better-sqlite3
```

### Database Schema
```sql
-- schema.sql

-- Drivers table
CREATE TABLE drivers (
    id INTEGER PRIMARY KEY,
    number INTEGER UNIQUE NOT NULL,
    name TEXT NOT NULL,
    team TEXT,
    circuit_fit_score INTEGER
);

-- Season statistics
CREATE TABLE season_stats (
    driver_id INTEGER PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    podiums INTEGER DEFAULT 0,
    top5 INTEGER DEFAULT 0,
    top10 INTEGER DEFAULT 0,
    dnfs INTEGER DEFAULT 0,
    total_races INTEGER DEFAULT 0,
    fastest_laps INTEGER DEFAULT 0,
    pole_positions INTEGER DEFAULT 0,
    avg_finish REAL,
    avg_qualifying REAL,
    points INTEGER DEFAULT 0,
    FOREIGN KEY (driver_id) REFERENCES drivers(id)
);

-- Race results
CREATE TABLE race_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    round INTEGER NOT NULL,
    date TEXT,
    start_position INTEGER,
    finish_position INTEGER,
    positions_gained INTEGER GENERATED ALWAYS AS (start_position - finish_position) STORED,
    fastest_lap_time TEXT,
    fastest_lap_rank INTEGER,
    gap_to_leader TEXT,
    gap_to_winner TEXT,
    laps_completed INTEGER,
    incident_points INTEGER DEFAULT 0,
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (track_id) REFERENCES tracks(id),
    UNIQUE(driver_id, round)
);

-- Tracks
CREATE TABLE tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    length_miles REAL,
    turns INTEGER,
    track_type TEXT -- 'road', 'street', 'oval'
);

-- Driver factors (overall and per track)
CREATE TABLE driver_factors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER NOT NULL,
    track_id INTEGER, -- NULL for overall
    consistency_value INTEGER,
    consistency_percentile INTEGER,
    racecraft_value INTEGER,
    racecraft_percentile INTEGER,
    raw_speed_value INTEGER,
    raw_speed_percentile INTEGER,
    tire_mgmt_value INTEGER,
    tire_mgmt_percentile INTEGER,
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (track_id) REFERENCES tracks(id),
    UNIQUE(driver_id, track_id)
);

-- Factor variables (detailed breakdown)
CREATE TABLE factor_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER NOT NULL,
    factor_name TEXT NOT NULL,
    variable_name TEXT NOT NULL,
    value INTEGER,
    percentile INTEGER,
    FOREIGN KEY (driver_id) REFERENCES drivers(id)
);

-- Skill simulations (store results)
CREATE TABLE skill_simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    driver_id INTEGER NOT NULL,
    consistency_adjustment INTEGER,
    racecraft_adjustment INTEGER,
    raw_speed_adjustment INTEGER,
    tire_mgmt_adjustment INTEGER,
    similar_driver_id INTEGER,
    similarity_score REAL,
    projected_position INTEGER,
    projected_wins INTEGER,
    projected_podiums INTEGER,
    projected_points INTEGER,
    coaching_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (similar_driver_id) REFERENCES drivers(id)
);

-- Indexes for performance
CREATE INDEX idx_race_results_driver ON race_results(driver_id);
CREATE INDEX idx_race_results_round ON race_results(round);
CREATE INDEX idx_driver_factors_driver ON driver_factors(driver_id);
CREATE INDEX idx_factor_variables_driver ON factor_variables(driver_id);
```

### Data Loading Script
```typescript
// scripts/loadData.ts
import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';

const db = new Database('circuit-fit.db');

// Create schema
const schema = fs.readFileSync('schema.sql', 'utf8');
db.exec(schema);

// Load data from provisional results
function loadProvisionalResults() {
  const resultsDir = './data/provisional_results';
  const files = fs.readdirSync(resultsDir);
  
  // Prepare statements for better performance
  const insertRace = db.prepare(`
    INSERT INTO race_results (
      driver_id, track_id, round, date,
      start_position, finish_position,
      fastest_lap_time, gap_to_leader
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const insertBatch = db.transaction((races) => {
    for (const race of races) {
      insertRace.run(race);
    }
  });
  
  // Process each race file
  files.forEach((file, round) => {
    const data = JSON.parse(
      fs.readFileSync(path.join(resultsDir, file), 'utf8')
    );
    
    const races = data.results.map(result => [
      result.driverNumber,  // driver_id
      getTrackId(data.track), // track_id
      round + 1,  // round
      data.date,  // date
      result.startPosition,
      result.finishPosition,
      result.fastestLap,
      result.gap
    ]);
    
    insertBatch(races);
  });
}

// Calculate and store season stats
function calculateSeasonStats() {
  const updateStats = db.prepare(`
    INSERT INTO season_stats (
      driver_id, wins, podiums, top5, top10,
      total_races, avg_finish, points
    )
    SELECT 
      driver_id,
      SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) as wins,
      SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) as podiums,
      SUM(CASE WHEN finish_position <= 5 THEN 1 ELSE 0 END) as top5,
      SUM(CASE WHEN finish_position <= 10 THEN 1 ELSE 0 END) as top10,
      COUNT(*) as total_races,
      AVG(finish_position) as avg_finish,
      SUM(
        CASE finish_position
          WHEN 1 THEN 50
          WHEN 2 THEN 40
          WHEN 3 THEN 35
          WHEN 4 THEN 32
          WHEN 5 THEN 30
          WHEN 6 THEN 28
          WHEN 7 THEN 26
          WHEN 8 THEN 24
          WHEN 9 THEN 22
          WHEN 10 THEN 20
          WHEN 11 THEN 19
          WHEN 12 THEN 18
          WHEN 13 THEN 17
          WHEN 14 THEN 16
          WHEN 15 THEN 15
          WHEN 16 THEN 14
          WHEN 17 THEN 13
          WHEN 18 THEN 12
          WHEN 19 THEN 11
          WHEN 20 THEN 10
          ELSE 10 - (finish_position - 20)
        END
      ) as points
    FROM race_results
    GROUP BY driver_id
  `);
  
  updateStats.run();
}

// Load driver factors from your analysis
function loadDriverFactors() {
  const factors = JSON.parse(
    fs.readFileSync('./data/driver_factors.json', 'utf8')
  );
  
  const insertFactor = db.prepare(`
    INSERT INTO driver_factors (
      driver_id, track_id,
      consistency_value, consistency_percentile,
      racecraft_value, racecraft_percentile,
      raw_speed_value, raw_speed_percentile,
      tire_mgmt_value, tire_mgmt_percentile
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  Object.entries(factors).forEach(([driverId, data]) => {
    // Insert overall factors
    insertFactor.run(
      driverId, null, // null track_id for overall
      data.overall.consistency.value,
      data.overall.consistency.percentile,
      data.overall.racecraft.value,
      data.overall.racecraft.percentile,
      data.overall.raw_speed.value,
      data.overall.raw_speed.percentile,
      data.overall.tire_mgmt.value,
      data.overall.tire_mgmt.percentile
    );
  });
}

// Run all loaders
loadProvisionalResults();
calculateSeasonStats();
loadDriverFactors();

console.log('Database loaded successfully!');
```

---

## Option 2: Runtime Calculations (No Database)

If you want to avoid ANY database setup, just calculate everything at runtime:

```typescript
// lib/dataProcessor.ts

interface ProcessedData {
  seasonStats: Map<number, SeasonStats>;
  raceResults: Map<number, RaceResult[]>;
  driverFactors: Map<number, DriverFactors>;
}

class DataProcessor {
  private cache: ProcessedData | null = null;
  
  async loadAllData(): Promise<ProcessedData> {
    if (this.cache) return this.cache;
    
    // Load all provisional results files
    const resultsFiles = await this.loadProvisionalResults();
    
    // Process into data structures
    const seasonStats = this.calculateSeasonStats(resultsFiles);
    const raceResults = this.extractRaceResults(resultsFiles);
    const driverFactors = await this.loadFactors();
    
    this.cache = {
      seasonStats,
      raceResults,
      driverFactors
    };
    
    return this.cache;
  }
  
  private calculateSeasonStats(results: any[]): Map<number, SeasonStats> {
    const stats = new Map();
    
    results.forEach(race => {
      race.results.forEach(driver => {
        if (!stats.has(driver.number)) {
          stats.set(driver.number, {
            wins: 0,
            podiums: 0,
            top5: 0,
            top10: 0,
            totalRaces: 0,
            points: 0
          });
        }
        
        const driverStats = stats.get(driver.number);
        driverStats.totalRaces++;
        
        if (driver.position === 1) driverStats.wins++;
        if (driver.position <= 3) driverStats.podiums++;
        if (driver.position <= 5) driverStats.top5++;
        if (driver.position <= 10) driverStats.top10++;
        
        driverStats.points += this.calculatePoints(driver.position);
      });
    });
    
    return stats;
  }
  
  private calculatePoints(position: number): number {
    const pointsMap = [50,40,35,32,30,28,26,24,22,20,19,18,17,16,15,14,13,12,11,10];
    return pointsMap[position - 1] || Math.max(0, 10 - (position - 20));
  }
}

// Singleton instance
export const dataProcessor = new DataProcessor();

// React hook for easy usage
export function useRaceData() {
  const [data, setData] = useState<ProcessedData | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    dataProcessor.loadAllData().then(data => {
      setData(data);
      setLoading(false);
    });
  }, []);
  
  return { data, loading };
}
```

---

## API Layer (Works with Either Option)

```typescript
// pages/api/driver/[id]/stats.ts
import { db } from '@/lib/database'; // SQLite option
// OR
import { dataProcessor } from '@/lib/dataProcessor'; // Runtime option

export default async function handler(req, res) {
  const { id } = req.query;
  
  // SQLite version
  const stats = db.prepare(`
    SELECT * FROM season_stats WHERE driver_id = ?
  `).get(id);
  
  // OR Runtime version
  const data = await dataProcessor.loadAllData();
  const stats = data.seasonStats.get(parseInt(id));
  
  res.json(stats);
}
```

---

## Skill Simulator (Works Offline)

```typescript
// lib/simulator.ts

export function simulateSkillReallocation(
  currentFactors: DriverFactors,
  adjustments: Adjustments
) {
  // All calculations done in-memory
  const newFactors = {
    consistency: currentFactors.consistency + adjustments.consistency,
    racecraft: currentFactors.racecraft + adjustments.racecraft,
    rawSpeed: currentFactors.rawSpeed + adjustments.rawSpeed,
    tireMgmt: currentFactors.tireMgmt + adjustments.tireMgmt
  };
  
  // Find most similar driver (no database needed)
  const allDrivers = getAllDriverFactors(); // From JSON
  const similarDriver = findMostSimilar(newFactors, allDrivers);
  
  // Project results based on similar driver
  const projectedResults = {
    championshipPos: similarDriver.seasonStats.finalPosition,
    avgFinish: similarDriver.seasonStats.avgFinish,
    wins: Math.round(similarDriver.seasonStats.wins * 1.1),
    podiums: Math.round(similarDriver.seasonStats.podiums * 1.1),
    points: Math.round(similarDriver.seasonStats.points * 1.05)
  };
  
  return {
    newFactors,
    similarDriver,
    projectedResults
  };
}
```

---

## Quick Start Commands

```bash
# Option 1: SQLite
npm install better-sqlite3
npm run load-data  # Populates SQLite from provisional results
npm run dev        # Start Next.js

# Option 2: Runtime (No Database)
npm install
npm run dev        # Everything calculated on the fly

# For production (either option)
npm run build
npm start
```

---

## Why This Approach Wins

1. **SQLite = Real Database** (Shows technical depth without complexity)
2. **Pre-processed Data** (Fast queries, no mock data)
3. **Git-Friendly** (Database is just a file)
4. **Offline-First** (No internet needed for demo)
5. **Easy Deployment** (Vercel handles SQLite files)

---

## Data Flow

```
Provisional Results (CSV/JSON files)
    ↓
Load Script (runs once)
    ↓
SQLite Database (circuit-fit.db)
    ↓
API Routes (Next.js)
    ↓
React Components
```

No PostgreSQL server, no Docker, no environment variables. Just works!
