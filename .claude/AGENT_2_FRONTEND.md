# Agent 2: Frontend & Product Development

## Mission
Build intuitive web application for visualizing driver skills, track fit, and delivering insights.

## Timeline
Days 8-28 (Weeks 2-4)

## Dependencies
- Outputs from Agent 1 (available Day 14):
  - `driver_metrics.json`
  - `track_profiles.json`
- React 18 + Vite
- Node.js 18+

## Tech Stack

### Core
- **Framework:** React 18 + Vite
- **Routing:** React Router v6
- **State:** Zustand (lightweight)
- **Styling:** Tailwind CSS + shadcn/ui

### Visualization
- **Charts:** Recharts (spider graphs)
- **Advanced:** Plotly.js (optional for advanced viz)

### Deployment
- **Platform:** Netlify
- **Functions:** Netlify serverless functions for API

## Project Structure

```
/driver-dna-trackfit/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn components
│   │   ├── SpiderGraph.jsx
│   │   ├── TrackFitMatrix.jsx
│   │   ├── DriverDashboard.jsx
│   │   └── CoachingReport.jsx
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── DriverProfile.jsx
│   │   ├── TrackComparison.jsx
│   │   └── CoachingHub.jsx
│   ├── lib/
│   │   ├── api.js
│   │   └── utils.js
│   ├── data/               # JSON from Agent 1
│   │   ├── driver_metrics.json
│   │   └── track_profiles.json
│   ├── App.jsx
│   └── main.jsx
├── netlify/
│   └── functions/
├── public/
├── index.html
├── package.json
├── tailwind.config.js
└── vite.config.js
```

## Phase 1: Project Setup (Days 8-10)

### Tasks

#### 1. Initialize project
```bash
# Create Vite project
npm create vite@latest driver-dna-trackfit -- --template react
cd driver-dna-trackfit

# Install dependencies
npm install react-router-dom zustand
npm install recharts
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install shadcn/ui
npx shadcn-ui@latest init
```

#### 2. Configure Tailwind
**File:** `tailwind.config.js`

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        // Add more colors as needed
      },
    },
  },
  plugins: [],
}
```

#### 3. Setup routing
**File:** `src/App.jsx`

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import DriverProfile from './pages/DriverProfile';
import TrackComparison from './pages/TrackComparison';
import CoachingHub from './pages/CoachingHub';
import Navbar from './components/Navbar';

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/driver/:driverId" element={<DriverProfile />} />
            <Route path="/compare" element={<TrackComparison />} />
            <Route path="/coaching/:driverId/:trackId" element={<CoachingHub />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

#### 4. Create data loading utility
**File:** `src/lib/api.js`

```javascript
// Load static JSON data
let driverMetrics = null;
let trackProfiles = null;

export async function loadDriverMetrics() {
  if (!driverMetrics) {
    const response = await fetch('/data/driver_metrics.json');
    driverMetrics = await response.json();
  }
  return driverMetrics;
}

export async function loadTrackProfiles() {
  if (!trackProfiles) {
    const response = await fetch('/data/track_profiles.json');
    trackProfiles = await response.json();
  }
  return trackProfiles;
}

export async function getDriver(driverId) {
  const data = await loadDriverMetrics();
  return data.drivers[driverId];
}

export async function getTrack(trackId) {
  const data = await loadTrackProfiles();
  return data.tracks[trackId];
}

export async function getAllDrivers() {
  const data = await loadDriverMetrics();
  return Object.values(data.drivers);
}

export async function getAllTracks() {
  const data = await loadTrackProfiles();
  return Object.values(data.tracks);
}

export function calculateFitScore(driverMetrics, trackDemands) {
  const attributes = [
    'qualifying_pace',
    'passing_efficiency',
    'corner_mastery',
    'racecraft',
    'consistency'
  ];
  
  let fitScore = 0;
  let totalWeight = 0;
  
  for (const attr of attributes) {
    const driverScore = driverMetrics[attr].score;
    const trackDemand = trackDemands[attr];
    
    // Weight by track demand importance
    const weight = trackDemand / 10;
    
    // Contribution: driver strength × track importance
    fitScore += driverScore * weight;
    totalWeight += weight;
  }
  
  return totalWeight > 0 ? fitScore / totalWeight : 5.0;
}
```

### Deliverables
- [ ] Project initialized
- [ ] Dependencies installed
- [ ] Routing configured
- [ ] Data loading utilities created

## Phase 2: Core Components (Days 11-17)

### Component 1: Spider Graph

**File:** `src/components/SpiderGraph.jsx`

```jsx
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend } from 'recharts';

export function SpiderGraph({ driverData, trackDemands = null, title = "Driver Skills" }) {
  const attributes = [
    { key: 'qualifying_pace', label: 'Qualifying Pace' },
    { key: 'passing_efficiency', label: 'Passing' },
    { key: 'corner_mastery', label: 'Cornering' },
    { key: 'racecraft', label: 'Racecraft' },
    { key: 'consistency', label: 'Consistency' }
  ];
  
  // Prepare data for Recharts
  const chartData = attributes.map(attr => {
    const point = {
      attribute: attr.label,
      driver: driverData[attr.key].score,
    };
    
    if (trackDemands) {
      point.track = trackDemands[attr.key];
    }
    
    return point;
  });
  
  return (
    <div className="w-full">
      <h3 className="text-lg font-semibold mb-4 text-center">{title}</h3>
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="attribute" />
          <PolarRadiusAxis angle={90} domain={[0, 10]} />
          
          <Radar
            name="Driver"
            dataKey="driver"
            stroke="#2563EB"
            fill="#2563EB"
            fillOpacity={0.6}
          />
          
          {trackDemands && (
            <Radar
              name="Track Demand"
              dataKey="track"
              stroke="#10B981"
              fill="#10B981"
              fillOpacity={0.2}
              strokeDasharray="5 5"
            />
          )}
          
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
      
      {/* Attribute details */}
      <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
        {attributes.map(attr => (
          <div key={attr.key} className="flex justify-between">
            <span className="text-muted-foreground">{attr.label}:</span>
            <span className="font-medium">
              {driverData[attr.key].score}/10
              <span className="text-muted-foreground ml-1">
                ({driverData[attr.key].percentile}th %)
              </span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Component 2: Track Fit Matrix

**File:** `src/components/TrackFitMatrix.jsx`

```jsx
import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { calculateFitScore } from '../lib/api';

export function TrackFitMatrix({ drivers, tracks }) {
  const navigate = useNavigate();
  const [sortBy, setSortBy] = useState('name');
  
  // Calculate fit scores for all combinations
  const fitScores = useMemo(() => {
    const scores = {};
    
    drivers.forEach(driver => {
      scores[driver.id] = {};
      
      tracks.forEach(track => {
        const driverMetrics = driver.tracks[track.id];
        if (driverMetrics) {
          scores[driver.id][track.id] = calculateFitScore(
            driverMetrics,
            track.demands
          );
        }
      });
    });
    
    return scores;
  }, [drivers, tracks]);
  
  // Get color for fit score
  const getFitColor = (score) => {
    if (score >= 8) return 'bg-green-600';
    if (score >= 6) return 'bg-green-400';
    if (score >= 4) return 'bg-yellow-400';
    return 'bg-red-400';
  };
  
  const handleCellClick = (driverId, trackId) => {
    navigate(`/coaching/${driverId}/${trackId}`);
  };
  
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <th className="border p-2 bg-muted">Driver</th>
            {tracks.map(track => (
              <th key={track.id} className="border p-2 bg-muted">
                {track.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {drivers.map(driver => (
            <tr key={driver.id}>
              <td className="border p-2 font-medium">
                {driver.name || driver.id}
              </td>
              {tracks.map(track => {
                const score = fitScores[driver.id]?.[track.id];
                
                return (
                  <td
                    key={track.id}
                    className={`border p-2 cursor-pointer transition-opacity hover:opacity-80 ${getFitColor(score)}`}
                    onClick={() => handleCellClick(driver.id, track.id)}
                    title={`Click for detailed analysis`}
                  >
                    <div className="text-center text-white font-semibold">
                      {score ? score.toFixed(1) : 'N/A'}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      
      <div className="mt-4 flex gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-600"></div>
          <span>Excellent (8-10)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-400"></div>
          <span>Good (6-8)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-400"></div>
          <span>Moderate (4-6)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-400"></div>
          <span>Poor (0-4)</span>
        </div>
      </div>
    </div>
  );
}
```

### Component 3: Driver Dashboard

**File:** `src/components/DriverDashboard.jsx`

```jsx
import { useState } from 'react';
import { SpiderGraph } from './SpiderGraph';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';

export function DriverDashboard({ driver, tracks }) {
  const [selectedTrack, setSelectedTrack] = useState(null);
  
  // Get driver's track data
  const availableTracks = Object.keys(driver.tracks);
  const currentTrack = selectedTrack || availableTracks[0];
  const driverMetrics = driver.tracks[currentTrack];
  const trackProfile = tracks.find(t => t.id === currentTrack);
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">
            {driver.name || driver.id}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Track</p>
              <Select value={currentTrack} onValueChange={setSelectedTrack}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {availableTracks.map(trackId => {
                    const track = tracks.find(t => t.id === trackId);
                    return (
                      <SelectItem key={trackId} value={trackId}>
                        {track?.name || trackId}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Spider Graph */}
      <Card>
        <CardContent className="pt-6">
          <SpiderGraph
            driverData={driverMetrics}
            trackDemands={trackProfile?.demands}
            title={`Skills at ${trackProfile?.name || currentTrack}`}
          />
        </CardContent>
      </Card>
      
      {/* Strengths & Weaknesses */}
      <Card>
        <CardHeader>
          <CardTitle>Strengths & Weaknesses</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold text-green-600 mb-2">Strengths</h4>
              <ul className="space-y-1">
                {Object.entries(driverMetrics)
                  .filter(([_, data]) => data.score >= 7)
                  .sort((a, b) => b[1].score - a[1].score)
                  .slice(0, 3)
                  .map(([attr, data]) => (
                    <li key={attr} className="text-sm">
                      • {attr.replace('_', ' ')}: {data.score}/10 ({data.percentile}th %)
                    </li>
                  ))}
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-red-600 mb-2">Areas for Improvement</h4>
              <ul className="space-y-1">
                {Object.entries(driverMetrics)
                  .filter(([_, data]) => data.score < 7)
                  .sort((a, b) => a[1].score - b[1].score)
                  .slice(0, 3)
                  .map(([attr, data]) => (
                    <li key={attr} className="text-sm">
                      • {attr.replace('_', ' ')}: {data.score}/10 ({data.percentile}th %)
                    </li>
                  ))}
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

### Deliverables
- [ ] Spider graph component working
- [ ] Track fit matrix displaying correctly
- [ ] Driver dashboard integrated
- [ ] Responsive design (mobile + desktop)

## Phase 3: Pages (Days 18-21)

### Page 1: Home
**File:** `src/pages/Home.jsx`

```jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { loadDriverMetrics, loadTrackProfiles } from '../lib/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';

export default function Home() {
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    async function loadStats() {
      const drivers = await loadDriverMetrics();
      const tracks = await loadTrackProfiles();
      
      setStats({
        driverCount: Object.keys(drivers.drivers).length,
        trackCount: Object.keys(tracks.tracks).length
      });
    }
    
    loadStats();
  }, []);
  
  return (
    <div className="max-w-4xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-5xl font-bold mb-4">
          DriverDNA × TrackFit
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          Match Your Skills to Track Demands
        </p>
        <p className="text-lg mb-8">
          Data-driven driver performance analysis for GR Cup racing
        </p>
        
        <div className="flex gap-4 justify-center">
          <Link to="/driver/D001">
            <Button size="lg">Explore Drivers</Button>
          </Link>
          <Link to="/compare">
            <Button size="lg" variant="outline">Compare Tracks</Button>
          </Link>
        </div>
      </div>
      
      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-3 gap-4 my-12">
          <Card>
            <CardHeader>
              <CardTitle className="text-center">{stats.driverCount}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-center text-muted-foreground">Drivers Analyzed</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-center">{stats.trackCount}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-center text-muted-foreground">Tracks Profiled</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-center">0.4s</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-center text-muted-foreground">Avg Improvement</p>
            </CardContent>
          </Card>
        </div>
      )}
      
      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6 my-12">
        <Card>
          <CardHeader>
            <CardTitle>5D Skill Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              Comprehensive analysis of qualifying pace, passing, cornering, racecraft, and consistency
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Track Fit Scoring</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              See which tracks suit your driving style and where you'll be most competitive
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>AI Coaching</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              Get personalized recommendations on what to practice and where you'll gain time
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

### Page 2: Driver Profile
**File:** `src/pages/DriverProfile.jsx`

```jsx
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getDriver, getAllTracks } from '../lib/api';
import { DriverDashboard } from '../components/DriverDashboard';
import { Button } from '../components/ui/button';

export default function DriverProfile() {
  const { driverId } = useParams();
  const [driver, setDriver] = useState(null);
  const [tracks, setTracks] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadData() {
      try {
        const driverData = await getDriver(driverId);
        const tracksData = await getAllTracks();
        
        setDriver(driverData);
        setTracks(tracksData);
      } catch (error) {
        console.error('Error loading driver:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, [driverId]);
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!driver) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-4">Driver Not Found</h2>
        <Link to="/">
          <Button>Back to Home</Button>
        </Link>
      </div>
    );
  }
  
  return (
    <div>
      <div className="mb-6">
        <Link to="/">
          <Button variant="outline">← Back</Button>
        </Link>
      </div>
      
      <DriverDashboard driver={driver} tracks={tracks} />
    </div>
  );
}
```

### Page 3: Coaching Hub
**File:** `src/pages/CoachingHub.jsx`

```jsx
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getDriver, getTrack } from '../lib/api';
import { Button } from '../components/ui/button';

export default function CoachingHub() {
  const { driverId, trackId } = useParams();
  const [driver, setDriver] = useState(null);
  const [track, setTrack] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadData() {
      try {
        const driverData = await getDriver(driverId);
        const trackData = await getTrack(trackId);
        
        setDriver(driverData);
        setTrack(trackData);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, [driverId, trackId]);
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <div>
      <div className="mb-6">
        <Link to={`/driver/${driverId}`}>
          <Button variant="outline">← Back to Driver</Button>
        </Link>
      </div>
      
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">
          Coaching Report: {driver?.name || driverId} at {track?.name || trackId}
        </h1>
        
        <p className="text-muted-foreground mb-8">
          Coaching recommendations will be displayed here once Agent 3 (Coaching Engine) is complete.
        </p>
        
        {/* This will be populated by Agent 3's output */}
      </div>
    </div>
  );
}
```

### Deliverables
- [ ] All pages created
- [ ] Navigation working
- [ ] Loading states implemented
- [ ] Error handling added

## Phase 4: Integration & Polish (Days 22-28)

### Tasks

#### 1. Integrate Coaching Reports (Days 22-24)
- Wait for Agent 3 to provide coaching report format
- Create `CoachingReport.jsx` component
- Display in CoachingHub page

#### 2. Performance Optimization (Day 25)
- Lazy load pages with React.lazy
- Optimize bundle size
- Add loading skeletons

**File:** `src/App.jsx` (updated)

```jsx
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';

// Lazy load pages
const Home = lazy(() => import('./pages/Home'));
const DriverProfile = lazy(() => import('./pages/DriverProfile'));
const TrackComparison = lazy(() => import('./pages/TrackComparison'));
const CoachingHub = lazy(() => import('./pages/CoachingHub'));

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Suspense fallback={<div>Loading...</div>}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/driver/:driverId" element={<DriverProfile />} />
              <Route path="/compare" element={<TrackComparison />} />
              <Route path="/coaching/:driverId/:trackId" element={<CoachingHub />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
```

#### 3. Responsive Design (Day 26)
- Test on mobile, tablet, desktop
- Adjust layouts for small screens
- Ensure touch targets are large enough

#### 4. Polish UI (Day 27)
- Add transitions and animations
- Improve loading states
- Add tooltips and help text
- Ensure accessibility

#### 5. Deploy to Netlify (Day 28)

**File:** `netlify.toml`

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"
```

**Deployment Steps:**
1. Push code to GitHub
2. Connect repository to Netlify
3. Configure build settings
4. Deploy

### Deliverables
- [ ] Coaching reports integrated
- [ ] Performance optimized (load < 2s)
- [ ] Responsive on all devices
- [ ] Deployed to Netlify
- [ ] Production URL working

## Final Checklist

### Components
- [ ] SpiderGraph working with real data
- [ ] TrackFitMatrix displaying fit scores
- [ ] DriverDashboard showing insights
- [ ] CoachingReport integrated (from Agent 3)

### Pages
- [ ] Home page welcoming and informative
- [ ] Driver Profile functional
- [ ] Coaching Hub displaying reports
- [ ] Track Comparison working

### Technical
- [ ] All routes navigating correctly
- [ ] Data loading from JSON files
- [ ] Error handling in place
- [ ] Loading states smooth
- [ ] Mobile responsive
- [ ] Accessibility (keyboard nav, ARIA labels)

### Deployment
- [ ] Builds successfully
- [ ] Deployed to Netlify
- [ ] All pages accessible
- [ ] No console errors

## Integration Points

### With Agent 1 (Data Science)
- **Input:** `driver_metrics.json`, `track_profiles.json`
- **Location:** Place in `public/data/` directory
- **Access:** Via `fetch()` in `lib/api.js`

### With Agent 3 (Coaching)
- **Input:** `coaching_report.json` format
- **Component:** Create `CoachingReport.jsx` to display
- **Page:** Integrate into `CoachingHub.jsx`

## Questions or Issues?

If you encounter:
- **Design questions:** Follow shadcn/ui patterns
- **Performance issues:** Use React DevTools profiler
- **Deployment problems:** Check Netlify build logs

See `PROJECT_PLAN.md` for overall context.
