# Scout Landing Page - Component Architecture & Implementation Guide

## Overview

This document provides detailed component specifications, props interfaces, and implementation guidelines for building the Scout Landing Page and enhanced Driver Detail views.

---

## Directory Structure

```
frontend/src/
├── pages/
│   ├── Scout/
│   │   ├── ScoutLanding.jsx              # Main landing page
│   │   ├── ScoutLanding.css
│   │   ├── ComparisonView.jsx            # Side-by-side comparison
│   │   ├── ComparisonView.css
│   │   └── index.js
│   │
│   ├── Overview/
│   │   ├── Overview.jsx                  # ENHANCED with scout context
│   │   └── Overview.css
│   │
│   └── [RaceLog, Skills, Improve]        # Existing, minimally modified
│
├── components/
│   ├── DriverCard/
│   │   ├── DriverCard.jsx                # Scout grid card
│   │   ├── DriverCard.css
│   │   └── index.js
│   │
│   ├── ClassificationBadge/
│   │   ├── ClassificationBadge.jsx       # FRONTRUNNER, CONTENDER badges
│   │   ├── ClassificationBadge.css
│   │   └── index.js
│   │
│   ├── DriverHeader/
│   │   ├── DriverHeader.jsx              # Enhanced detail page header
│   │   ├── DriverHeader.css
│   │   └── index.js
│   │
│   ├── FilterSidebar/
│   │   ├── FilterSidebar.jsx             # Scout filter controls
│   │   ├── FilterSidebar.css
│   │   └── index.js
│   │
│   ├── ComparisonDrawer/
│   │   ├── ComparisonDrawer.jsx          # Bottom drawer with queue
│   │   ├── ComparisonDrawer.css
│   │   └── index.js
│   │
│   ├── ScoutNavBar/
│   │   ├── ScoutNavBar.jsx               # Top navigation bar
│   │   ├── ScoutNavBar.css
│   │   └── index.js
│   │
│   └── FactorBar/
│       ├── FactorBar.jsx                 # Horizontal bar chart
│       ├── FactorBar.css
│       └── index.js
│
├── context/
│   ├── ScoutContext.jsx                  # NEW: Scout state management
│   └── DriverContext.jsx                 # ENHANCED: Add scout awareness
│
├── hooks/
│   ├── useScoutState.js                  # Scout state persistence
│   ├── useDriverData.js                  # Driver data fetching/caching
│   └── useComparisonQueue.js             # Comparison queue management
│
├── utils/
│   ├── classification.js                 # Classification logic
│   ├── filtering.js                      # Filter application functions
│   └── formatting.js                     # Number/stat formatting
│
└── App.jsx                                # UPDATED: New routing structure
```

---

## Context Architecture

### 1. ScoutContext (NEW)

**Purpose:** Manage scout landing page state (filters, comparison queue, view preferences)

**File:** `/frontend/src/context/ScoutContext.jsx`

```jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const ScoutContext = createContext(null);

export const ScoutProvider = ({ children }) => {
  // Filter state
  const [filters, setFilters] = useState({
    classifications: [], // ['FRONTRUNNER', 'CONTENDER', 'MID_PACK', 'DEVELOPMENT']
    speedRange: [0, 100],
    consistencyRange: [0, 100],
    racecraftRange: [0, 100],
    tireMgmtRange: [0, 100],
    experienceLevel: 'all', // 'all' | 'veterans' | 'developing' | 'rookies'
    searchQuery: ''
  });

  // View state
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'table'
  const [sortBy, setSortBy] = useState('overall_score'); // 'overall_score' | 'speed' | 'consistency' | 'racecraft'
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc' | 'desc'
  const [scrollPosition, setScrollPosition] = useState(0);

  // Comparison queue (max 4 drivers)
  const [comparisonQueue, setComparisonQueue] = useState([]);

  // Recently viewed drivers (last 5)
  const [recentlyViewed, setRecentlyViewed] = useState([]);

  // Persist state to sessionStorage
  useEffect(() => {
    const state = {
      filters,
      viewMode,
      sortBy,
      sortOrder,
      scrollPosition,
      comparisonQueue,
      recentlyViewed
    };
    sessionStorage.setItem('scoutState', JSON.stringify(state));
  }, [filters, viewMode, sortBy, sortOrder, scrollPosition, comparisonQueue, recentlyViewed]);

  // Restore state from sessionStorage on mount
  useEffect(() => {
    const savedState = sessionStorage.getItem('scoutState');
    if (savedState) {
      const state = JSON.parse(savedState);
      setFilters(state.filters || filters);
      setViewMode(state.viewMode || 'grid');
      setSortBy(state.sortBy || 'overall_score');
      setSortOrder(state.sortOrder || 'desc');
      setScrollPosition(state.scrollPosition || 0);
      setComparisonQueue(state.comparisonQueue || []);
      setRecentlyViewed(state.recentlyViewed || []);
    }
  }, []);

  // Filter manipulation functions
  const updateFilter = (filterName, value) => {
    setFilters(prev => ({ ...prev, [filterName]: value }));
  };

  const toggleClassification = (classification) => {
    setFilters(prev => ({
      ...prev,
      classifications: prev.classifications.includes(classification)
        ? prev.classifications.filter(c => c !== classification)
        : [...prev.classifications, classification]
    }));
  };

  const resetFilters = () => {
    setFilters({
      classifications: [],
      speedRange: [0, 100],
      consistencyRange: [0, 100],
      racecraftRange: [0, 100],
      tireMgmtRange: [0, 100],
      experienceLevel: 'all',
      searchQuery: ''
    });
  };

  // Comparison queue management
  const addToComparison = (driverNumber) => {
    if (comparisonQueue.length >= 4) {
      alert('Comparison queue full (max 4 drivers). Remove a driver to add another.');
      return;
    }
    if (!comparisonQueue.includes(driverNumber)) {
      setComparisonQueue(prev => [...prev, driverNumber]);
    }
  };

  const removeFromComparison = (driverNumber) => {
    setComparisonQueue(prev => prev.filter(num => num !== driverNumber));
  };

  const clearComparisonQueue = () => {
    setComparisonQueue([]);
  };

  // Recently viewed management
  const addToRecentlyViewed = (driverNumber) => {
    setRecentlyViewed(prev => {
      const filtered = prev.filter(item => item.driverNumber !== driverNumber);
      const newItem = { driverNumber, timestamp: Date.now() };
      return [newItem, ...filtered].slice(0, 5); // Keep last 5
    });
  };

  const value = {
    // Filter state
    filters,
    updateFilter,
    toggleClassification,
    resetFilters,

    // View state
    viewMode,
    setViewMode,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,
    scrollPosition,
    setScrollPosition,

    // Comparison
    comparisonQueue,
    addToComparison,
    removeFromComparison,
    clearComparisonQueue,

    // Recently viewed
    recentlyViewed,
    addToRecentlyViewed
  };

  return (
    <ScoutContext.Provider value={value}>
      {children}
    </ScoutContext.Provider>
  );
};

export const useScout = () => {
  const context = useContext(ScoutContext);
  if (!context) {
    throw new Error('useScout must be used within ScoutProvider');
  }
  return context;
};
```

### 2. Enhanced DriverContext

**File:** `/frontend/src/context/DriverContext.jsx` (ENHANCED)

Add these fields to existing DriverContext:

```jsx
// ADD TO EXISTING DriverContext:

const [isFromScout, setIsFromScout] = useState(false);
const [scoutReturnPath, setScoutReturnPath] = useState('/scout');

// Navigation helpers
const navigateToDriver = (driverNumber, fromScout = true) => {
  setSelectedDriverNumber(driverNumber);
  setIsFromScout(fromScout);
  setScoutReturnPath('/scout');
};

const returnToScout = () => {
  setIsFromScout(false);
  // Navigation handled by component (uses useNavigate)
};

// Add to value:
const value = {
  // ... existing fields
  isFromScout,
  setIsFromScout,
  scoutReturnPath,
  navigateToDriver,
  returnToScout
};
```

---

## Core Components

### 1. ScoutLanding Component

**Purpose:** Main scout landing page with driver grid and filters

**Props:** None (uses ScoutContext and DriverContext)

**File:** `/frontend/src/pages/Scout/ScoutLanding.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useScout } from '../../context/ScoutContext';
import { useDriver } from '../../context/DriverContext';
import DriverCard from '../../components/DriverCard/DriverCard';
import FilterSidebar from '../../components/FilterSidebar/FilterSidebar';
import ComparisonDrawer from '../../components/ComparisonDrawer/ComparisonDrawer';
import ScoutNavBar from '../../components/ScoutNavBar/ScoutNavBar';
import api from '../../services/api';
import { applyFilters, applySorting } from '../../utils/filtering';
import './ScoutLanding.css';

export default function ScoutLanding() {
  const navigate = useNavigate();
  const {
    filters,
    viewMode,
    sortBy,
    sortOrder,
    comparisonQueue,
    setScrollPosition
  } = useScout();
  const { drivers, setSelectedDriverNumber, setIsFromScout } = useDriver();

  const [filteredDrivers, setFilteredDrivers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Apply filters and sorting whenever they change
  useEffect(() => {
    if (drivers.length > 0) {
      const filtered = applyFilters(drivers, filters);
      const sorted = applySorting(filtered, sortBy, sortOrder);
      setFilteredDrivers(sorted);
      setLoading(false);
    }
  }, [drivers, filters, sortBy, sortOrder]);

  // Restore scroll position on mount
  useEffect(() => {
    const savedState = sessionStorage.getItem('scoutState');
    if (savedState) {
      const state = JSON.parse(savedState);
      if (state.scrollPosition) {
        setTimeout(() => {
          window.scrollTo({ top: state.scrollPosition, behavior: 'smooth' });
        }, 100);
      }
    }
  }, []);

  // Save scroll position on scroll
  useEffect(() => {
    const handleScroll = () => {
      setScrollPosition(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [setScrollPosition]);

  const handleDriverClick = (driverNumber) => {
    setSelectedDriverNumber(driverNumber);
    setIsFromScout(true);
    navigate(`/scout/driver/${driverNumber}/overview`);
  };

  if (loading) {
    return (
      <div className="scout-landing">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading drivers...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="scout-landing">
      <ScoutNavBar />
      <div className="scout-content">
        <FilterSidebar />
        <div className="scout-main">
          <div className="results-header">
            <h2>
              {filteredDrivers.length === drivers.length
                ? `All Drivers (${drivers.length})`
                : `${filteredDrivers.length} of ${drivers.length} Drivers`}
            </h2>
            {filters.classifications.length > 0 && (
              <div className="active-filters">
                {filters.classifications.map(c => (
                  <span key={c} className="filter-badge">{c}</span>
                ))}
              </div>
            )}
          </div>

          {viewMode === 'grid' ? (
            <div className="driver-grid">
              {filteredDrivers.map(driver => (
                <DriverCard
                  key={driver.driver_number}
                  driver={driver}
                  onClick={() => handleDriverClick(driver.driver_number)}
                  isInComparison={comparisonQueue.includes(driver.driver_number)}
                />
              ))}
            </div>
          ) : (
            <div className="driver-table">
              {/* Table view implementation */}
            </div>
          )}

          {filteredDrivers.length === 0 && (
            <div className="no-results">
              <h3>No drivers match your filters</h3>
              <p>Try adjusting your criteria or reset all filters.</p>
            </div>
          )}
        </div>
      </div>
      {comparisonQueue.length > 0 && <ComparisonDrawer />}
    </div>
  );
}
```

**CSS Highlights:**

```css
/* ScoutLanding.css */
.scout-landing {
  min-height: 100vh;
  background: #0a0a0a;
  color: #fff;
}

.scout-content {
  display: flex;
  gap: 24px;
  max-width: 1600px;
  margin: 0 auto;
  padding: 24px;
}

.scout-main {
  flex: 1;
}

.driver-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .driver-grid {
    grid-template-columns: 1fr;
  }
}
```

---

### 2. DriverCard Component

**Purpose:** Driver card shown in scout grid

**Props:**
```typescript
interface DriverCardProps {
  driver: Driver;
  onClick: () => void;
  isInComparison: boolean;
}
```

**File:** `/frontend/src/components/DriverCard/DriverCard.jsx`

```jsx
import React from 'react';
import ClassificationBadge from '../ClassificationBadge/ClassificationBadge';
import FactorBar from '../FactorBar/FactorBar';
import { useScout } from '../../context/ScoutContext';
import './DriverCard.css';

export default function DriverCard({ driver, onClick, isInComparison }) {
  const { addToComparison, removeFromComparison } = useScout();

  const handleCompareClick = (e) => {
    e.stopPropagation(); // Prevent card click
    if (isInComparison) {
      removeFromComparison(driver.driver_number);
    } else {
      addToComparison(driver.driver_number);
    }
  };

  return (
    <div className="driver-card" onClick={onClick}>
      <ClassificationBadge classification={driver.classification} />

      <div className="driver-number">{driver.driver_number}</div>
      <h3 className="driver-name">Driver #{driver.driver_number}</h3>
      <p className="driver-series">Toyota Gazoo Series</p>

      <div className="overall-stat">
        <div className="stat-label">Overall Score</div>
        <div className="stat-value">{driver.overall_score}</div>
        <div className="stat-percentile">
          {driver.percentile.toFixed(1)}th Percentile
        </div>
      </div>

      <div className="factor-bars">
        <FactorBar
          label="Speed"
          value={driver.factors.speed.percentile}
        />
        <FactorBar
          label="Consistency"
          value={driver.factors.consistency.percentile}
        />
        <FactorBar
          label="Racecraft"
          value={driver.factors.racecraft.percentile}
        />
        <FactorBar
          label="Tire Mgmt"
          value={driver.factors.tire_management.percentile}
        />
      </div>

      <div className="quick-stats">
        <span>{driver.stats.race_count} Races</span>
        <span>{driver.stats.avg_finish.toFixed(2)} Avg</span>
        <span>{driver.stats.podiums} Podiums</span>
      </div>

      <div className="card-actions" onClick={(e) => e.stopPropagation()}>
        <button className="btn-view-details">View Details →</button>
        <button
          className={`btn-compare ${isInComparison ? 'active' : ''}`}
          onClick={handleCompareClick}
        >
          {isInComparison ? '✓ Added' : '+ Compare'}
        </button>
      </div>
    </div>
  );
}
```

**CSS Highlights:**

```css
/* DriverCard.css */
.driver-card {
  background: #ffffff;
  border: 4px solid #e74c3c;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 16px rgba(231, 76, 60, 0.3);
}

.driver-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 24px rgba(231, 76, 60, 0.4);
  border-color: #ff5e4e;
}

.driver-number {
  font-size: 72px;
  font-weight: 900;
  text-align: center;
  color: #000;
  line-height: 1;
  margin: 16px 0;
}

.overall-stat {
  background: #f5f5f5;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  margin: 16px 0;
}

.stat-value {
  font-size: 48px;
  font-weight: 900;
  color: #e74c3c;
  line-height: 1;
}

.card-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn-view-details {
  flex: 1;
  padding: 12px;
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-view-details:hover {
  background: #c0392b;
}

.btn-compare {
  padding: 12px 16px;
  background: #fff;
  color: #e74c3c;
  border: 2px solid #e74c3c;
  border-radius: 8px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-compare.active {
  background: #e74c3c;
  color: #fff;
}
```

---

### 3. ClassificationBadge Component

**Purpose:** Display driver classification badge (FRONTRUNNER, CONTENDER, etc.)

**Props:**
```typescript
interface ClassificationBadgeProps {
  classification: 'FRONTRUNNER' | 'CONTENDER' | 'MID_PACK' | 'DEVELOPMENT';
  centered?: boolean;
}
```

**File:** `/frontend/src/components/ClassificationBadge/ClassificationBadge.jsx`

```jsx
import React from 'react';
import './ClassificationBadge.css';

const CLASSIFICATION_COLORS = {
  FRONTRUNNER: '#FFD700',
  CONTENDER: '#C0C0C0',
  MID_PACK: '#CD7F32',
  DEVELOPMENT: '#718096'
};

const CLASSIFICATION_LABELS = {
  FRONTRUNNER: 'FRONTRUNNER',
  CONTENDER: 'CONTENDER',
  MID_PACK: 'MID-PACK',
  DEVELOPMENT: 'DEVELOPMENT'
};

export default function ClassificationBadge({ classification, centered = false }) {
  const backgroundColor = CLASSIFICATION_COLORS[classification] || '#718096';
  const label = CLASSIFICATION_LABELS[classification] || classification;
  const textColor = classification === 'MID_PACK' ? '#fff' : '#000';

  return (
    <div
      className={`classification-badge ${centered ? 'centered' : ''}`}
      style={{
        backgroundColor,
        color: textColor
      }}
    >
      {label}
    </div>
  );
}
```

**CSS:**

```css
/* ClassificationBadge.css */
.classification-badge {
  display: inline-block;
  padding: 8px 20px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.classification-badge.centered {
  padding: 12px 32px;
  border-radius: 18px;
  font-size: 14px;
  display: block;
  text-align: center;
  max-width: 300px;
  margin: 0 auto;
}
```

---

### 4. Enhanced DriverHeader Component

**Purpose:** Enhanced header for driver detail pages with scout context

**File:** `/frontend/src/components/DriverHeader/DriverHeader.jsx`

```jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useDriver } from '../../context/DriverContext';
import ClassificationBadge from '../ClassificationBadge/ClassificationBadge';
import './DriverHeader.css';

export default function DriverHeader({ driver }) {
  const navigate = useNavigate();
  const {
    selectedDriverNumber,
    setSelectedDriverNumber,
    drivers,
    isFromScout
  } = useDriver();

  const handleBackToScout = () => {
    navigate('/scout');
  };

  const handleDriverChange = (e) => {
    const newDriverNumber = Number(e.target.value);
    setSelectedDriverNumber(newDriverNumber);
    navigate(`/scout/driver/${newDriverNumber}/overview`);
  };

  return (
    <div className="driver-header-enhanced">
      {/* Top Navigation Bar */}
      <div className="header-nav">
        <button className="back-to-scout" onClick={handleBackToScout}>
          ← Scout Portal
        </button>
        <div className="quick-actions">
          <button className="btn-compare-action">Compare with Others</button>
          <select
            value={selectedDriverNumber}
            onChange={handleDriverChange}
            className="driver-selector"
          >
            {drivers.map(d => (
              <option key={d.number} value={d.number}>
                Driver #{d.number}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Classification Badge */}
      <div className="classification-section">
        <ClassificationBadge
          classification={driver.classification}
          centered
        />
      </div>

      {/* Driver Identity */}
      <div className="driver-identity">
        <div className="driver-number-badge">{driver.driver_number}</div>
        <div className="driver-info">
          <h1>Driver #{driver.driver_number}</h1>
          <p className="series-name">Toyota Gazoo Series</p>
        </div>
        <div className="driver-stats-summary">
          <div>
            Overall: {driver.overall_score} ({driver.percentile.toFixed(1)}th %ile)
          </div>
          <div>
            {driver.stats.race_count} Races | {driver.stats.avg_finish.toFixed(2)} Avg Finish
          </div>
        </div>
      </div>
    </div>
  );
}
```

**CSS:**

```css
/* DriverHeader.css */
.driver-header-enhanced {
  background: #1a1a1a;
  padding: 24px;
  margin-bottom: 24px;
}

.header-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.back-to-scout {
  background: none;
  border: none;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

.back-to-scout:hover {
  opacity: 0.7;
  text-decoration: underline;
}

.quick-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.classification-section {
  margin: 24px 0;
}

.driver-identity {
  display: flex;
  align-items: center;
  gap: 24px;
}

.driver-number-badge {
  width: 100px;
  height: 100px;
  background: #e74c3c;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  font-weight: 900;
  color: #fff;
  border: 4px solid #fff;
}

.driver-info h1 {
  font-size: 36px;
  font-weight: 800;
  margin: 0;
  color: #fff;
}

.driver-stats-summary {
  margin-left: auto;
  text-align: right;
  font-size: 16px;
  font-weight: 600;
  color: #e0e0e0;
}
```

---

### 5. FilterSidebar Component

**Purpose:** Filter controls for scout landing page

**File:** `/frontend/src/components/FilterSidebar/FilterSidebar.jsx`

```jsx
import React from 'react';
import { useScout } from '../../context/ScoutContext';
import './FilterSidebar.css';

export default function FilterSidebar() {
  const {
    filters,
    toggleClassification,
    updateFilter,
    resetFilters
  } = useScout();

  const classifications = [
    { value: 'FRONTRUNNER', label: 'Frontrunners', count: 1 },
    { value: 'CONTENDER', label: 'Contenders', count: 7 },
    { value: 'MID_PACK', label: 'Mid-Pack', count: 15 },
    { value: 'DEVELOPMENT', label: 'Development', count: 11 }
  ];

  return (
    <div className="filter-sidebar">
      <h3>Filters</h3>

      {/* Classification Filters */}
      <div className="filter-group">
        <h4>Classification</h4>
        {classifications.map(({ value, label, count }) => (
          <label key={value} className="filter-checkbox">
            <input
              type="checkbox"
              checked={filters.classifications.includes(value)}
              onChange={() => toggleClassification(value)}
            />
            <span>{label} ({count})</span>
          </label>
        ))}
      </div>

      {/* Speed Range */}
      <div className="filter-group">
        <h4>Raw Speed</h4>
        <input
          type="range"
          min="0"
          max="100"
          value={filters.speedRange[1]}
          onChange={(e) => updateFilter('speedRange', [0, Number(e.target.value)])}
        />
        <div className="range-labels">
          <span>0</span>
          <span>{filters.speedRange[1]}</span>
        </div>
      </div>

      {/* Experience Level */}
      <div className="filter-group">
        <h4>Experience</h4>
        <label className="filter-radio">
          <input
            type="radio"
            name="experience"
            value="all"
            checked={filters.experienceLevel === 'all'}
            onChange={(e) => updateFilter('experienceLevel', e.target.value)}
          />
          <span>All Drivers</span>
        </label>
        <label className="filter-radio">
          <input
            type="radio"
            name="experience"
            value="veterans"
            checked={filters.experienceLevel === 'veterans'}
            onChange={(e) => updateFilter('experienceLevel', e.target.value)}
          />
          <span>Veterans (10+ races)</span>
        </label>
        <label className="filter-radio">
          <input
            type="radio"
            name="experience"
            value="rookies"
            checked={filters.experienceLevel === 'rookies'}
            onChange={(e) => updateFilter('experienceLevel', e.target.value)}
          />
          <span>Rookies (&lt;5 races)</span>
        </label>
      </div>

      {/* Reset Button */}
      <button className="btn-reset-filters" onClick={resetFilters}>
        Reset All Filters
      </button>
    </div>
  );
}
```

---

### 6. ComparisonDrawer Component

**Purpose:** Bottom drawer showing comparison queue

**File:** `/frontend/src/components/ComparisonDrawer/ComparisonDrawer.jsx`

```jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useScout } from '../../context/ScoutContext';
import { useDriver } from '../../context/DriverContext';
import './ComparisonDrawer.css';

export default function ComparisonDrawer() {
  const navigate = useNavigate();
  const { comparisonQueue, removeFromComparison, clearComparisonQueue } = useScout();
  const { drivers } = useDriver();

  const handleCompare = () => {
    const driverIds = comparisonQueue.join(',');
    navigate(`/scout/compare?drivers=${driverIds}`);
  };

  const getDriverByNumber = (number) => {
    return drivers.find(d => d.driver_number === number);
  };

  return (
    <div className="comparison-drawer">
      <div className="drawer-header">
        <h3>Comparison Queue ({comparisonQueue.length} selected)</h3>
        <button className="btn-compare-now" onClick={handleCompare} disabled={comparisonQueue.length < 2}>
          Compare Now →
        </button>
      </div>
      <div className="drawer-content">
        {comparisonQueue.map(driverNumber => {
          const driver = getDriverByNumber(driverNumber);
          return (
            <div key={driverNumber} className="comparison-item">
              <div className="item-number">#{driverNumber}</div>
              <button
                className="btn-remove"
                onClick={() => removeFromComparison(driverNumber)}
              >
                ✕
              </button>
            </div>
          );
        })}
        {comparisonQueue.length < 4 && (
          <div className="comparison-item add-more">
            <div className="add-icon">+</div>
            <div className="add-label">Add Driver</div>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## Utility Functions

### filtering.js

```javascript
// /frontend/src/utils/filtering.js

export const applyFilters = (drivers, filters) => {
  let filtered = [...drivers];

  // Classification filter
  if (filters.classifications.length > 0) {
    filtered = filtered.filter(d =>
      filters.classifications.includes(d.classification)
    );
  }

  // Speed range filter
  filtered = filtered.filter(d =>
    d.factors.speed.percentile >= filters.speedRange[0] &&
    d.factors.speed.percentile <= filters.speedRange[1]
  );

  // Experience level filter
  if (filters.experienceLevel === 'veterans') {
    filtered = filtered.filter(d => d.stats.race_count >= 10);
  } else if (filters.experienceLevel === 'rookies') {
    filtered = filtered.filter(d => d.stats.race_count < 5);
  }

  // Search query filter
  if (filters.searchQuery) {
    const query = filters.searchQuery.toLowerCase();
    filtered = filtered.filter(d =>
      d.driver_number.toString().includes(query) ||
      `driver ${d.driver_number}`.includes(query)
    );
  }

  return filtered;
};

export const applySorting = (drivers, sortBy, sortOrder) => {
  const sorted = [...drivers].sort((a, b) => {
    let aVal, bVal;

    switch (sortBy) {
      case 'overall_score':
        aVal = a.overall_score;
        bVal = b.overall_score;
        break;
      case 'speed':
        aVal = a.factors.speed.percentile;
        bVal = b.factors.speed.percentile;
        break;
      case 'consistency':
        aVal = a.factors.consistency.percentile;
        bVal = b.factors.consistency.percentile;
        break;
      case 'racecraft':
        aVal = a.factors.racecraft.percentile;
        bVal = b.factors.racecraft.percentile;
        break;
      default:
        return 0;
    }

    return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
  });

  return sorted;
};
```

---

## Routing Updates

### App.jsx (UPDATED)

```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { DriverProvider } from './context/DriverContext';
import { ScoutProvider } from './context/ScoutContext';

// Import pages
import ScoutLanding from './pages/Scout/ScoutLanding';
import ComparisonView from './pages/Scout/ComparisonView';
import Overview from './pages/Overview/Overview';
import RaceLog from './pages/RaceLog/RaceLog';
import Skills from './pages/Skills/Skills';
import Improve from './pages/Improve/Improve';

function App() {
  return (
    <Router>
      <DriverProvider>
        <ScoutProvider>
          <div className="app min-h-screen bg-bg-primary">
            <main>
              <Routes>
                {/* Scout Routes */}
                <Route path="/" element={<Navigate to="/scout" replace />} />
                <Route path="/scout" element={<ScoutLanding />} />
                <Route path="/scout/compare" element={<ComparisonView />} />

                {/* Driver Detail Routes */}
                <Route path="/scout/driver/:driverNumber/overview" element={<Overview />} />
                <Route path="/scout/driver/:driverNumber/race-log" element={<RaceLog />} />
                <Route path="/scout/driver/:driverNumber/skills" element={<Skills />} />
                <Route path="/scout/driver/:driverNumber/improve" element={<Improve />} />

                {/* Legacy Routes (Redirect) */}
                <Route path="/overview" element={<Navigate to="/scout/driver/13/overview" replace />} />
                <Route path="/race-log" element={<Navigate to="/scout/driver/13/race-log" replace />} />
                <Route path="/skills" element={<Navigate to="/scout/driver/13/skills" replace />} />
                <Route path="/improve" element={<Navigate to="/scout/driver/13/improve" replace />} />
              </Routes>
            </main>
          </div>
        </ScoutProvider>
      </DriverProvider>
    </Router>
  );
}

export default App;
```

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Create ScoutContext with state management
- [ ] Build FilterSidebar component
- [ ] Build DriverCard component
- [ ] Build ClassificationBadge component
- [ ] Create ScoutLanding page with grid layout
- [ ] Connect to existing driver API

### Phase 2: Enhanced Header
- [ ] Build DriverHeader component
- [ ] Update Overview page to use DriverHeader
- [ ] Add "← Scout Portal" back button
- [ ] Integrate classification badges

### Phase 3: Comparison Feature
- [ ] Build ComparisonDrawer component
- [ ] Add comparison queue to ScoutContext
- [ ] Build ComparisonView page
- [ ] Implement side-by-side comparison table
- [ ] Add radar chart overlay

### Phase 4: Routing & Navigation
- [ ] Update App.jsx with new routes
- [ ] Implement legacy route redirects
- [ ] Add state persistence (sessionStorage)
- [ ] Build navigation transitions

### Phase 5: Polish
- [ ] Mobile responsive design
- [ ] Keyboard navigation
- [ ] Loading states
- [ ] Error handling
- [ ] Analytics instrumentation

---

**Document Version:** 1.0
**Last Updated:** 2025-11-02
**Companion Documents:**
- SCOUT_TO_OVERVIEW_USER_JOURNEY.md
- SCOUT_JOURNEY_VISUAL_FLOW.md
