import React, { createContext, useContext, useState, useEffect } from 'react';

const ScoutContext = createContext();

export function ScoutProvider({ children }) {
  // Filter state
  const [filters, setFilters] = useState({
    classification: [], // ["FRONTRUNNER", "CONTENDER", "MID_PACK", "DEVELOPMENT"]
    experience: [],     // ["VETERAN", "DEVELOPING", "ROOKIE"]
    attributes: [],     // ["SPEED", "WHEEL_TO_WHEEL", "CONSISTENT"]
    overallRange: [30, 70],
    speedRange: [0, 100],
    racesRange: [0, 15],
    avgFinishRange: [1, 25],
    searchQuery: ''
  });

  // View state
  const [view, setView] = useState('cards'); // 'cards' | 'table'
  const [sortBy, setSortBy] = useState('overall_score');
  const [sortOrder, setSortOrder] = useState('desc');

  // Comparison queue (max 4 drivers)
  const [comparisonQueue, setComparisonQueue] = useState([]);

  // Selected drivers for bulk actions
  const [selectedDrivers, setSelectedDrivers] = useState([]);

  // Restore state from sessionStorage on mount
  useEffect(() => {
    const savedState = sessionStorage.getItem('scoutState');
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState);
        setFilters(parsed.filters || filters);
        setView(parsed.view || 'cards');
        setSortBy(parsed.sortBy || 'overall_score');
        setSortOrder(parsed.sortOrder || 'desc');
        setComparisonQueue(parsed.comparisonQueue || []);
      } catch (error) {
        console.error('Failed to restore scout state:', error);
      }
    }
  }, []);

  // Save state to sessionStorage whenever it changes
  useEffect(() => {
    const stateToSave = {
      filters,
      view,
      sortBy,
      sortOrder,
      comparisonQueue
    };
    sessionStorage.setItem('scoutState', JSON.stringify(stateToSave));
  }, [filters, view, sortBy, sortOrder, comparisonQueue]);

  // Filter functions
  const updateFilter = (filterKey, value) => {
    setFilters(prev => ({
      ...prev,
      [filterKey]: value
    }));
  };

  const resetFilters = () => {
    setFilters({
      classification: [],
      experience: [],
      attributes: [],
      overallRange: [30, 70],
      speedRange: [0, 100],
      racesRange: [0, 15],
      avgFinishRange: [1, 25],
      searchQuery: ''
    });
  };

  // Comparison queue functions
  const addToComparison = (driverNumber) => {
    if (comparisonQueue.length >= 4) {
      alert('Maximum 4 drivers can be compared at once');
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

  // Selection functions (single-select only)
  const toggleDriverSelection = (driverNumber) => {
    setSelectedDrivers(prev =>
      prev.includes(driverNumber)
        ? [] // Deselect if clicking same driver
        : [driverNumber] // Select only this driver (single-select)
    );
  };

  const selectAllDrivers = (driverNumbers) => {
    setSelectedDrivers(driverNumbers);
  };

  const clearSelection = () => {
    setSelectedDrivers([]);
  };

  const value = {
    // State
    filters,
    view,
    sortBy,
    sortOrder,
    comparisonQueue,
    selectedDrivers,

    // Filter actions
    updateFilter,
    resetFilters,

    // View actions
    setView,
    setSortBy,
    setSortOrder,

    // Comparison actions
    addToComparison,
    removeFromComparison,
    clearComparisonQueue,

    // Selection actions
    toggleDriverSelection,
    selectAllDrivers,
    clearSelection
  };

  return (
    <ScoutContext.Provider value={value}>
      {children}
    </ScoutContext.Provider>
  );
}

export function useScout() {
  const context = useContext(ScoutContext);
  if (!context) {
    throw new Error('useScout must be used within ScoutProvider');
  }
  return context;
}
