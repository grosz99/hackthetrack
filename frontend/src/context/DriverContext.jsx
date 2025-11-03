import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const DriverContext = createContext();

export const useDriver = () => {
  const context = useContext(DriverContext);
  if (!context) {
    throw new Error('useDriver must be used within DriverProvider');
  }
  return context;
};

export const DriverProvider = ({ children }) => {
  const [selectedDriverNumber, setSelectedDriverNumber] = useState(13);
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load all drivers on mount
  useEffect(() => {
    const loadDrivers = async () => {
      try {
        const response = await api.get('/api/drivers');
        const driversList = response.data
          .sort((a, b) => a.driver_number - b.driver_number)
          .map(d => ({
            // Basic info
            number: d.driver_number,
            name: d.driver_name || `Driver #${d.driver_number}`,

            // Performance metrics
            overall_score: d.overall_score || 0,
            speed: d.speed?.score || 0,
            consistency: d.consistency?.score || 0,
            racecraft: d.racecraft?.score || 0,
            tire_management: d.tire_management?.score || 0,

            // Stats
            races: d.stats?.races_completed || 0,
            avg_finish: d.stats?.average_finish || 0,
            best_finish: d.stats?.best_finish || 0,
            worst_finish: d.stats?.worst_finish || 0,

            // Factor details (for classification)
            factors: {
              raw_speed: {
                score: d.speed?.score || 0,
                percentile: d.speed?.percentile || 0
              },
              consistency: {
                score: d.consistency?.score || 0,
                percentile: d.consistency?.percentile || 0
              },
              racecraft: {
                score: d.racecraft?.score || 0,
                percentile: d.racecraft?.percentile || 0
              },
              tire_mgmt: {
                score: d.tire_management?.score || 0,
                percentile: d.tire_management?.percentile || 0
              }
            }
          }));
        setDrivers(driversList);
      } catch (error) {
        console.error('Failed to load drivers:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDrivers();
  }, []);

  const value = {
    selectedDriverNumber,
    setSelectedDriverNumber,
    drivers,
    loading
  };

  return (
    <DriverContext.Provider value={value}>
      {children}
    </DriverContext.Provider>
  );
};
