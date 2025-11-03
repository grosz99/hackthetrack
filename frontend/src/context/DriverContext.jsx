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
            number: d.driver_number,
            name: d.driver_name || `Driver #${d.driver_number}`
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
