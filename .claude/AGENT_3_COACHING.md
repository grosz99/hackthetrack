# Agent 3: AI Coaching Engine

## Mission
Build intelligent recommendation system that provides actionable coaching advice based on driver weaknesses and track demands.

## Timeline
Days 15-28 (Weeks 3-4)

## Dependencies
- Outputs from Agent 1 (available Day 14):
  - `driver_metrics.json`
  - `track_profiles.json`
- Python 3.10+
- Libraries: pandas, numpy

## Core Concept

The coaching engine identifies where a driver is weak AND the track demands strength, then provides:
1. **Specific telemetry-based insights** (not generic advice)
2. **Prioritized action items** (what to focus on)
3. **Structured practice plans** (how to allocate session time)
4. **Expected improvements** (quantified time gains)

## Architecture

```
Coaching Engine
├── Domain Knowledge Base (racing expertise encoded)
├── Gap Analysis Module (finds priorities)
├── Telemetry Insights Module (identifies specific issues)
├── Recommendation Generator (creates action plans)
└── Practice Plan Builder (structures sessions)
```

## Phase 1: Domain Knowledge Encoding (Days 15-18)

### Objective
Encode racing expertise into structured rules and data.

### Tasks

#### 1. Create domain knowledge base
**File:** `src/coaching/domain_knowledge.py`

```python
"""
Racing domain knowledge encoded as constants and rules.
This is where racing expertise gets codified.
"""

# === IMPROVEMENT PARAMETERS ===

# How difficult is each skill to improve? (1=easy, 10=very hard)
IMPROVEMENT_DIFFICULTY = {
    'qualifying_pace': 8,        # Raw speed is hardest
    'passing_efficiency': 6,      # Technique-based, medium
    'corner_mastery': 5,          # Practice pays off
    'racecraft': 7,               # Experience-dependent
    'consistency': 4              # Most improvable
}

# Expected lap time gain per skill point improvement (seconds/lap)
TIME_GAIN_PER_POINT = {
    'qualifying_pace': 0.20,      # Direct lap time impact
    'passing_efficiency': 0.08,   # Indirect (positioning)
    'corner_mastery': 0.15,       # Direct lap time
    'racecraft': 0.05,            # Race-long benefit
    'consistency': 0.10           # Reduces errors
}

# === TRACK-SPECIFIC KNOWLEDGE ===

# Critical corners at each track
CRITICAL_CORNERS = {
    'barber': {
        'name': 'Barber Motorsports Park',
        'focus_corners': [4, 9, 12, 16],
        'descriptions': {
            4: 'Exit onto back straight - maximize exit speed',
            9: 'Tricky chicane - late braking, smooth transition',
            12: 'Downhill left - trust grip and commit',
            16: 'Final corner - clean exit for start/finish line'
        },
        'passing_zones': [1, 5],
        'key_characteristic': 'Corner exit speed is everything'
    },
    'COTA': {
        'name': 'Circuit of the Americas',
        'focus_corners': [1, 11, 15, 19],
        'descriptions': {
            1: 'Uphill left-hander - carry speed, late apex',
            11: 'Hairpin - braking crucial, prioritize exit',
            15: 'Switchback complex - momentum through 15-16-17',
            19: 'Final corner - exit speed for main straight'
        },
        'passing_zones': [1, 11, 12],
        'key_characteristic': 'Qualifying pace critical - big track with few passing opportunities'
    },
    'sebring': {
        'name': 'Sebring International Raceway',
        'focus_corners': [1, 7, 10, 17],
        'descriptions': {
            1: 'Fast right-hander - commitment required',
            7: 'Hairpin - late braking, good exit',
            10: 'Technical section - precision needed',
            17: 'Final turn - set up for long straight'
        },
        'passing_zones': [1, 7, 17],
        'key_characteristic': 'Bumpy surface - consistency and car control matter'
    },
    'sonoma': {
        'name': 'Sonoma Raceway',
        'focus_corners': [2, 4, 7, 11],
        'descriptions': {
            2: 'Uphill right-hander - blind apex',
            4: 'Hairpin - late braking opportunity',
            7: 'Carousel - maintain momentum',
            11: 'Final corner - crucial for main straight'
        },
        'passing_zones': [1, 7],
        'key_characteristic': 'Elevation changes - brake points vary by session'
    },
    'VIR': {
        'name': 'Virginia International Raceway',
        'focus_corners': [1, 10, 13, 19],
        'descriptions': {
            1: 'Fast opening corner - sets tone for lap',
            10: 'Climbing esses - rhythm section',
            13: 'Oak Tree - commitment corner',
            19: 'Final corner - exit speed critical'
        },
        'passing_zones': [1, 14],
        'key_characteristic': 'High-speed flow - consistency and confidence'
    },
    'road_america': {
        'name': 'Road America',
        'focus_corners': [1, 5, 8, 14],
        'descriptions': {
            1: 'Turn 1 - heavy braking from high speed',
            5: 'Carousel - long sweeper, maintain momentum',
            8: 'Hurry Downs - technical downhill section',
            14: 'Last corner - critical for 1-mile straight'
        },
        'passing_zones': [1, 5, 14],
        'key_characteristic': 'Long straights - drafting and passing opportunities'
    }
}

# === IMPROVEMENT RECOMMENDATIONS ===

# Specific advice by skill and priority level
RECOMMENDATIONS = {
    'qualifying_pace': {
        'CRITICAL': [
            'Focus on clean, mistake-free laps - consistency is key',
            'Analyze your best lap telemetry - identify 3 corners where you lose most time',
            'Practice single-lap pace in qualifying simulations',
            'Study track evolution - track gets faster throughout session'
        ],
        'HIGH': [
            'Work on commitment in high-speed corners',
            'Optimize gear ratios for key acceleration zones',
            'Practice restarts to simulate qualifying intensity'
        ],
        'MEDIUM': [
            'Review qualifying footage to identify missed opportunities',
            'Work with engineer on optimal tire pressure for single lap'
        ]
    },
    'passing_efficiency': {
        'CRITICAL': [
            'Study your successful passes - what made them work?',
            'Practice different passing lines - inside vs outside',
            'Work on late braking - gain confidence in heavy braking zones',
            'Learn to use draft effectively - timing is everything'
        ],
        'HIGH': [
            'Focus on corner exit speed - faster exit = easier pass',
            'Practice defensive driving - understand how to position car',
            'Study opponent patterns - anticipate their moves'
        ],
        'MEDIUM': [
            'Review race footage - identify missed passing opportunities',
            'Work on racecraft in practice - simulate battles'
        ]
    },
    'corner_mastery': {
        'CRITICAL': [
            '70% of practice on corner exits - this is your biggest opportunity',
            'Film your laps - compare steering inputs to fast drivers',
            'Focus on smoothness - abrupt inputs cost time',
            'Learn to "rotate" the car - turn-in technique crucial'
        ],
        'HIGH': [
            'Practice trail braking to carry more speed',
            'Work on throttle application timing',
            'Study apex positioning - small changes, big gains'
        ],
        'MEDIUM': [
            'Focus on one corner per session - master it before moving on',
            'Work on consistency - hit same marks every lap'
        ]
    },
    'racecraft': {
        'CRITICAL': [
            'Practice defensive positioning - make your car wide',
            'Learn optimal racing line changes - when to deviate',
            'Work on situational awareness - mirrors and peripheral vision',
            'Study race strategy - when to attack, when to defend'
        ],
        'HIGH': [
            'Practice battling with teammates - safe environment',
            'Focus on clean racing - avoid contact',
            'Learn to read competitor body language (steering inputs)'
        ],
        'MEDIUM': [
            'Review race battles - what worked, what didn't',
            'Work on patience - don't force moves'
        ]
    },
    'consistency': {
        'CRITICAL': [
            'Establish reference points for every corner',
            'Practice mental visualization - rehearse perfect lap',
            'Focus on repeatable inputs - same every lap',
            'Work on physical fitness - fatigue kills consistency'
        ],
        'HIGH': [
            'Monitor lap time variance - target <0.4s standard deviation',
            'Practice tire management - smooth = fast over stint',
            'Develop pre-corner routines - triggers for each corner'
        ],
        'MEDIUM': [
            'Review practice data - identify inconsistent corners',
            'Work on mental training - stay present, avoid distractions'
        ]
    }
}

# === TRACK TYPE STRATEGIES ===

TRACK_TYPE_ADVICE = {
    'Technical Corner Track': {
        'priority_skills': ['corner_mastery', 'consistency'],
        'general_advice': [
            'Precision over aggression - smooth is fast',
            'Corner exit speed compounds through lap',
            'Limited passing - qualifying position critical',
            'Tire management crucial for race pace',
            'Focus on perfecting racing line'
        ]
    },
    'High-Speed Flow Track': {
        'priority_skills': ['qualifying_pace', 'consistency', 'passing_efficiency'],
        'general_advice': [
            'Commitment in high-speed corners pays dividends',
            'Drafting and slipstream are powerful - use them',
            'Multiple passing zones - racecraft matters',
            'Maintain momentum - avoid mid-corner braking',
            'Physical fitness important - high G-forces'
        ]
    },
    'Balanced Power Track': {
        'priority_skills': ['qualifying_pace', 'corner_mastery', 'passing_efficiency'],
        'general_advice': [
            'All skills matter - well-rounded performance required',
            'Strategic opportunities in both corners and straights',
            'Adapt to track evolution throughout session',
            'Balance risk vs reward - multiple lines work',
            'Racecraft opportunities abundant'
        ]
    },
    'Mixed Technical Track': {
        'priority_skills': ['corner_mastery', 'consistency', 'racecraft'],
        'general_advice': [
            'Adaptability key - different corner types',
            'Consistency more important than peak speed',
            'Strategic corner prioritization - focus on key corners',
            'Tire management critical - varied demands',
            'Learn track quirks - surface, bumps, camber'
        ]
    }
}

# === PRACTICE SESSION TEMPLATES ===

PRACTICE_DRILLS = {
    'corner_mastery': [
        {
            'name': 'Single Corner Focus',
            'duration': 10,
            'description': 'Focus solely on one corner for 10 laps',
            'objective': 'Perfect entry, apex, and exit'
        },
        {
            'name': 'Corner Sequence',
            'duration': 10,
            'description': 'Link 2-3 corners together smoothly',
            'objective': 'Maintain momentum through sequence'
        },
        {
            'name': 'Full Lap Integration',
            'duration': 10,
            'description': 'Put it all together - complete laps',
            'objective': 'Consistent execution every corner'
        }
    ],
    'consistency': [
        {
            'name': 'Reference Point Drill',
            'duration': 15,
            'description': 'Identify and hit reference points every lap',
            'objective': 'Build muscle memory'
        },
        {
            'name': 'Long Run',
            'duration': 20,
            'description': '20 consecutive clean laps',
            'objective': 'Lap time variance <0.4s'
        }
    ],
    'qualifying_pace': [
        {
            'name': 'Qualifying Simulation',
            'duration': 15,
            'description': '3 flying laps with cool-down between',
            'objective': 'Peak performance on demand'
        },
        {
            'name': 'Single Lap Focus',
            'duration': 10,
            'description': 'One perfect lap - no mistakes',
            'objective': 'Find absolute limit'
        }
    ]
}
```

### Deliverables
- [ ] Domain knowledge file created
- [ ] All tracks have corner priorities defined
- [ ] Recommendations written for all scenarios
- [ ] Racing expert (human) reviews and approves

## Phase 2: Coaching Engine Core (Days 19-24)

### Objective
Build the core recommendation engine.

### Tasks

#### 1. Create coaching engine
**File:** `src/coaching/coaching_engine.py`

```python
"""
Main coaching recommendation engine.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from domain_knowledge import *

class CoachingEngine:
    """Generates personalized coaching recommendations"""
    
    def __init__(self, driver_metrics_file='outputs/driver_metrics.json',
                 track_profiles_file='outputs/track_profiles.json'):
        
        # Load data
        with open(driver_metrics_file) as f:
            self.metrics_data = json.load(f)
        
        with open(track_profiles_file) as f:
            self.tracks_data = json.load(f)
    
    def generate_coaching_report(self, driver_id, track_id):
        """
        Main entry point - generates complete coaching report.
        
        Args:
            driver_id: Driver identifier
            track_id: Track identifier
        
        Returns:
            Complete coaching report dictionary
        """
        
        # Get data
        driver = self.metrics_data['drivers'][driver_id]
        driver_metrics = driver['tracks'][track_id]
        track = self.tracks_data['tracks'][track_id]
        
        # Run analysis
        gaps = self.analyze_gaps(driver_metrics, track['demands'])
        priorities = self.calculate_priorities(gaps)
        practice_plan = self.generate_practice_plan(priorities, track_id)
        expected_gains = self.calculate_expected_gains(priorities)
        summary = self.generate_executive_summary(
            driver, track, priorities, expected_gains
        )
        
        # Calculate fit score
        fit_score = self.calculate_fit_score(driver_metrics, track['demands'])
        
        # Build report
        report = {
            'driver_id': driver_id,
            'driver_name': driver.get('name', driver_id),
            'track_id': track_id,
            'track_name': track['name'],
            'generated_at': datetime.now().isoformat(),
            'summary': summary,
            'track_fit_score': round(fit_score, 1),
            'priorities': priorities,
            'practice_plan': practice_plan,
            'expected_gains': expected_gains
        }
        
        return report
    
    def analyze_gaps(self, driver_metrics, track_demands):
        """
        Identify skill gaps: (Track Demand - Driver Score)
        
        Returns list of gaps sorted by weighted importance
        """
        
        attributes = [
            'qualifying_pace',
            'passing_efficiency',
            'corner_mastery',
            'racecraft',
            'consistency'
        ]
        
        gaps = []
        
        for attr in attributes:
            driver_score = driver_metrics[attr]['score']
            track_demand = track_demands[attr]
            
            gap = track_demand - driver_score
            weighted_gap = gap * (track_demand / 10)  # Weight by importance
            
            priority = self._determine_priority(gap, track_demand)
            
            gaps.append({
                'skill': attr,
                'driver_score': round(driver_score, 1),
                'track_demand': round(track_demand, 1),
                'gap': round(gap, 2),
                'weighted_gap': round(weighted_gap, 2),
                'priority': priority
            })
        
        return sorted(gaps, key=lambda x: x['weighted_gap'], reverse=True)
    
    def _determine_priority(self, gap, demand):
        """Classify priority level"""
        if gap > 2.5 and demand > 7.5:
            return 'CRITICAL'
        elif gap > 1.5 and demand > 6.0:
            return 'HIGH'
        elif gap > 0.8:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def calculate_priorities(self, gaps):
        """
        Enhanced priority calculation.
        
        Considers:
        - Gap size
        - Track demand weight
        - Improvement difficulty
        - Potential time gain
        """
        
        top_priorities = []
        
        for gap_item in gaps[:3]:  # Top 3
            skill = gap_item['skill']
            
            # Potential time gain
            time_gain = gap_item['gap'] * TIME_GAIN_PER_POINT[skill]
            
            # Actionability (easier to improve = higher score)
            difficulty = IMPROVEMENT_DIFFICULTY[skill]
            actionability = (10 - difficulty) / 10
            
            # Priority score
            priority_score = (
                gap_item['weighted_gap'] * 
                time_gain * 
                actionability
            )
            
            gap_item['time_gain_potential'] = round(time_gain, 2)
            gap_item['actionability'] = round(actionability, 2)
            gap_item['priority_score'] = round(priority_score, 2)
            
            top_priorities.append(gap_item)
        
        return sorted(top_priorities, key=lambda x: x['priority_score'], reverse=True)
    
    def generate_practice_plan(self, priorities, track_id):
        """
        Create structured practice session plan.
        
        Allocates 60 minutes based on priority scores
        """
        
        total_time = 60  # minutes
        total_priority = sum(p['priority_score'] for p in priorities)
        
        if total_priority == 0:
            # Fallback if no priorities
            return {'sessions': [], 'total_duration': 0}
        
        sessions = []
        
        for i, priority in enumerate(priorities):
            skill = priority['skill']
            
            # Calculate time allocation
            time_allocation = int((priority['priority_score'] / total_priority) * total_time)
            
            # Get recommendations for this skill
            recommendations = RECOMMENDATIONS[skill][priority['priority']]
            
            # Get corner priorities if applicable
            corner_info = None
            if skill == 'corner_mastery' and track_id in CRITICAL_CORNERS:
                corner_info = CRITICAL_CORNERS[track_id]
            
            session = {
                'name': f"Session {i+1}: {skill.replace('_', ' ').title()}",
                'duration': time_allocation,
                'focus': skill,
                'objectives': recommendations,
                'expected_gain': f"{priority['time_gain_potential']:.2f}s"
            }
            
            # Add corner-specific advice
            if corner_info:
                session['focus_corners'] = corner_info['focus_corners']
                session['corner_details'] = corner_info['descriptions']
            
            # Add drills if available
            if skill in PRACTICE_DRILLS:
                session['drills'] = PRACTICE_DRILLS[skill]
            
            sessions.append(session)
        
        return {
            'total_duration': total_time,
            'sessions': sessions
        }
    
    def calculate_expected_gains(self, priorities):
        """Calculate total expected improvement"""
        
        total_gain = sum(p['time_gain_potential'] for p in priorities)
        
        return {
            'total_potential_gain': round(total_gain, 2),
            'breakdown': [
                {
                    'skill': p['skill'],
                    'gain': p['time_gain_potential']
                }
                for p in priorities
            ]
        }
    
    def generate_executive_summary(self, driver, track, priorities, expected_gains):
        """Create natural language summary"""
        
        track_name = track['name']
        top_priority = priorities[0]
        total_gain = expected_gains['total_potential_gain']
        
        # Build summary
        summary = (
            f"At {track_name}, your {top_priority['skill'].replace('_', ' ')} "
            f"({top_priority['driver_score']}/10) is below track demand "
            f"({top_priority['track_demand']}/10). "
        )
        
        # Add track-specific advice
        track_type = track['persona']
        if track_type in TRACK_TYPE_ADVICE:
            general_advice = TRACK_TYPE_ADVICE[track_type]['general_advice'][0]
            summary += f"{general_advice} "
        
        # Add focus recommendation
        if top_priority['skill'] == 'corner_mastery' and track['id'] in CRITICAL_CORNERS:
            corners = CRITICAL_CORNERS[track['id']]['focus_corners']
            summary += f"Focus on corners {', '.join(map(str, corners))}. "
        
        # Add expected gain
        summary += f"Expected improvement: {total_gain:.2f} seconds per lap."
        
        return summary
    
    def calculate_fit_score(self, driver_metrics, track_demands):
        """Calculate driver-track fit score"""
        
        attributes = [
            'qualifying_pace',
            'passing_efficiency',
            'corner_mastery',
            'racecraft',
            'consistency'
        ]
        
        fit_score = 0
        total_weight = 0
        
        for attr in attributes:
            driver_score = driver_metrics[attr]['score']
            track_demand = track_demands[attr]
            
            weight = track_demand / 10
            contribution = driver_score * weight
            
            fit_score += contribution
            total_weight += weight
        
        return fit_score / total_weight if total_weight > 0 else 5.0
    
    def save_report(self, report, output_dir='outputs/coaching_reports'):
        """Save coaching report to JSON"""
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{report['driver_id']}_{report['track_id']}_coaching_report.json"
        filepath = output_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Coaching report saved to {filepath}")
        
        return filepath
```

#### 2. Generate reports for all combinations
**File:** `src/coaching/generate_all_reports.py`

```python
"""
Generate coaching reports for all driver-track combinations.
"""

from coaching_engine import CoachingEngine
import json

def generate_all_coaching_reports():
    """Generate reports for all drivers at all tracks"""
    
    engine = CoachingEngine()
    
    drivers = engine.metrics_data['drivers']
    tracks = engine.tracks_data['tracks']
    
    print(f"Generating coaching reports for {len(drivers)} drivers × {len(tracks)} tracks...")
    
    report_count = 0
    
    for driver_id, driver_data in drivers.items():
        for track_id in driver_data['tracks'].keys():
            if track_id in tracks:
                print(f"  Generating: {driver_id} at {track_id}")
                
                report = engine.generate_coaching_report(driver_id, track_id)
                engine.save_report(report)
                
                report_count += 1
    
    print(f"\n✓ Generated {report_count} coaching reports")

if __name__ == '__main__':
    generate_all_coaching_reports()
```

### Deliverables
- [ ] Coaching engine implemented
- [ ] Gap analysis working
- [ ] Practice plans generated
- [ ] Reports saved to JSON

## Phase 3: Frontend Integration (Days 25-28)

### Objective
Display coaching reports in the web application.

### Tasks

#### 1. Create coaching report component
**File:** `src/frontend/components/CoachingReport.jsx`

```jsx
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';

export function CoachingReport({ report }) {
  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardContent className="pt-6">
          <h2 className="text-2xl font-bold mb-4">
            {report.driver_name} at {report.track_name}
          </h2>
          <p className="text-lg leading-relaxed mb-4">
            {report.summary}
          </p>
          <div className="flex gap-4">
            <Badge>Track Fit: {report.track_fit_score}/10</Badge>
            <Badge variant="outline">
              Potential Gain: {report.expected_gains.total_potential_gain}s/lap
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Priorities */}
      <Card>
        <CardHeader>
          <CardTitle>🎯 Priority Improvement Areas</CardTitle>
        </CardHeader>
        <CardContent>
          {report.priorities.map((priority, idx) => (
            <div key={idx} className="mb-6 last:mb-0">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold text-lg">
                  #{idx + 1}: {priority.skill.replace('_', ' ').toUpperCase()}
                </h3>
                <Badge variant={
                  priority.priority === 'CRITICAL' ? 'destructive' :
                  priority.priority === 'HIGH' ? 'default' : 'secondary'
                }>
                  {priority.priority}
                </Badge>
              </div>
              
              <div className="grid grid-cols-3 gap-4 text-sm mb-2">
                <div>
                  <span className="text-muted-foreground">Your Score:</span>
                  <span className="font-medium ml-2">{priority.driver_score}/10</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Track Demand:</span>
                  <span className="font-medium ml-2">{priority.track_demand}/10</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Potential Gain:</span>
                  <span className="font-medium ml-2">{priority.time_gain_potential}s</span>
                </div>
              </div>
              
              <div className="bg-muted p-3 rounded-md">
                <p className="text-sm font-medium mb-1">Gap: {priority.gap} points</p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Practice Plan */}
      <Card>
        <CardHeader>
          <CardTitle>📋 Practice Session Plan ({report.practice_plan.total_duration} minutes)</CardTitle>
        </CardHeader>
        <CardContent>
          {report.practice_plan.sessions.map((session, idx) => (
            <div key={idx} className="mb-6 last:mb-0">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">{session.name}</h3>
                <Badge>{session.duration} min</Badge>
              </div>
              
              <div className="ml-4 space-y-2">
                <div>
                  <p className="text-sm font-medium">Objectives:</p>
                  <ul className="list-disc list-inside text-sm text-muted-foreground">
                    {session.objectives.map((obj, i) => (
                      <li key={i}>{obj}</li>
                    ))}
                  </ul>
                </div>
                
                {session.focus_corners && (
                  <div>
                    <p className="text-sm font-medium">Focus Corners:</p>
                    <div className="text-sm text-muted-foreground">
                      {session.focus_corners.join(', ')}
                    </div>
                  </div>
                )}
                
                <div>
                  <p className="text-sm font-medium">Expected Gain:</p>
                  <p className="text-sm text-muted-foreground">{session.expected_gain}</p>
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Improvement Roadmap */}
      <Card>
        <CardHeader>
          <CardTitle>🚀 Expected Outcomes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <p className="text-lg font-semibold">
              Total Potential Improvement: {report.expected_gains.total_potential_gain} seconds per lap
            </p>
            <div className="text-sm text-muted-foreground">
              <p>By addressing these priority areas, you can significantly improve your performance at {report.track_name}.</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

#### 2. Load coaching report in page
**File:** `src/frontend/pages/CoachingHub.jsx` (update)

```jsx
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CoachingReport } from '../components/CoachingReport';
import { Button } from '../components/ui/button';

export default function CoachingHub() {
  const { driverId, trackId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadReport() {
      try {
        // Load coaching report
        const response = await fetch(
          `/data/coaching_reports/${driverId}_${trackId}_coaching_report.json`
        );
        
        if (!response.ok) {
          throw new Error('Report not found');
        }
        
        const data = await response.json();
        setReport(data);
      } catch (error) {
        console.error('Error loading coaching report:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadReport();
  }, [driverId, trackId]);
  
  if (loading) {
    return <div>Loading coaching report...</div>;
  }
  
  if (!report) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold mb-4">Coaching Report Not Found</h2>
        <Link to={`/driver/${driverId}`}>
          <Button>Back to Driver Profile</Button>
        </Link>
      </div>
    );
  }
  
  return (
    <div>
      <div className="mb-6">
        <Link to={`/driver/${driverId}`}>
          <Button variant="outline">← Back to Driver Profile</Button>
        </Link>
      </div>
      
      <CoachingReport report={report} />
    </div>
  );
}
```

### Deliverables
- [ ] CoachingReport component created
- [ ] Reports loading in CoachingHub page
- [ ] All sections displaying correctly
- [ ] Responsive design

## Final Checklist

### Domain Knowledge (Days 15-18)
- [ ] All tracks have corner priorities
- [ ] Recommendations written for all skills
- [ ] Track type advice documented
- [ ] Racing expert reviewed and approved

### Engine Core (Days 19-24)
- [ ] Gap analysis working
- [ ] Priority calculation accurate
- [ ] Practice plans generated
- [ ] Reports saved to JSON

### Frontend Integration (Days 25-28)
- [ ] CoachingReport component working
- [ ] Reports loading from JSON
- [ ] All data displaying correctly
- [ ] Mobile responsive

### Output Files
- [ ] Coaching reports generated for all driver-track combinations
- [ ] Reports placed in `public/data/coaching_reports/`
- [ ] Format matches frontend expectations

## Integration Points

### With Agent 1 (Data Science)
- **Input:** `driver_metrics.json`, `track_profiles.json`
- **Purpose:** Source data for gap analysis

### With Agent 2 (Frontend)
- **Output:** Coaching report JSON files
- **Location:** `public/data/coaching_reports/`
- **Component:** `CoachingReport.jsx` displays reports

## Questions or Issues?

If you encounter:
- **Domain knowledge gaps:** Consult `DOMAIN_KNOWLEDGE.md` or ask human expert
- **Algorithm issues:** Review gap analysis logic
- **Integration problems:** Check JSON format matches frontend expectations

See `PROJECT_PLAN.md` for overall context.
