import { createContext, useContext, useState, useEffect } from 'react';

const SelectionContext = createContext();

export function SelectionProvider({ children }) {
  const [selectedDriver, setSelectedDriver] = useState(() => {
    const saved = localStorage.getItem('selectedDriver');
    return saved ? parseInt(saved) : null;
  });

  const [selectedTrack, setSelectedTrack] = useState(() => {
    const saved = localStorage.getItem('selectedTrack');
    return saved || null;
  });

  const [comparisonDriver, setComparisonDriver] = useState(() => {
    const saved = localStorage.getItem('comparisonDriver');
    return saved ? parseInt(saved) : null;
  });

  // Persist to localStorage whenever values change
  useEffect(() => {
    if (selectedDriver) {
      localStorage.setItem('selectedDriver', selectedDriver.toString());
    } else {
      localStorage.removeItem('selectedDriver');
    }
  }, [selectedDriver]);

  useEffect(() => {
    if (selectedTrack) {
      localStorage.setItem('selectedTrack', selectedTrack);
    } else {
      localStorage.removeItem('selectedTrack');
    }
  }, [selectedTrack]);

  useEffect(() => {
    if (comparisonDriver) {
      localStorage.setItem('comparisonDriver', comparisonDriver.toString());
    } else {
      localStorage.removeItem('comparisonDriver');
    }
  }, [comparisonDriver]);

  const value = {
    selectedDriver,
    setSelectedDriver,
    selectedTrack,
    setSelectedTrack,
    comparisonDriver,
    setComparisonDriver,
    clearSelection: () => {
      setSelectedDriver(null);
      setSelectedTrack(null);
      setComparisonDriver(null);
    }
  };

  return (
    <SelectionContext.Provider value={value}>
      {children}
    </SelectionContext.Provider>
  );
}

export function useSelection() {
  const context = useContext(SelectionContext);
  if (!context) {
    throw new Error('useSelection must be used within SelectionProvider');
  }
  return context;
}
