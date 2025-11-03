import React from 'react';
/**
 * Navigation - Main navigation bar with driver selector
 *
 * PFF-style top navigation with 4 main sections
 */

import { NavLink } from 'react-router-dom';
import { useState, useEffect } from 'react';
import DriverSelector from './shared/DriverSelector';

function Navigation() {
  const [selectedDriver, setSelectedDriver] = useState(13); // Default to driver #13
  const [drivers, setDrivers] = useState([]);

  // Load drivers list (we'll connect to API later)
  useEffect(() => {
    // TODO: Fetch from API
    // For now, use sample data
    setDrivers([
      { driver_number: 13, name: 'Sarah Chen', team: 'Apex Racing', overall_rating: 95, grade: 'Elite' },
      { driver_number: 7, name: 'Marcus Rodriguez', team: 'Velocity Motorsports', overall_rating: 88, grade: 'Strong' },
      { driver_number: 72, name: 'Alex Thompson', team: 'Thunder Racing', overall_rating: 85, grade: 'Strong' },
      { driver_number: 22, name: 'Jordan Kim', team: 'Phoenix Racing', overall_rating: 75, grade: 'Average' },
      { driver_number: 88, name: 'Taylor Santos', team: 'Rising Star Racing', overall_rating: 68, grade: 'Average' },
      { driver_number: 45, name: 'Casey Morgan', team: 'Next Gen Racing', overall_rating: 62, grade: 'Average' },
      { driver_number: 33, name: 'Riley Park', team: 'Rookie Racing Team', overall_rating: 55, grade: 'Developing' },
      { driver_number: 51, name: 'Jamie Foster', team: 'Classic Racing', overall_rating: 65, grade: 'Average' },
    ]);
  }, []);

  const handleDriverChange = (driverNumber) => {
    setSelectedDriver(driverNumber);
    // TODO: Update global state or context
  };

  const navItems = [
    { to: '/overview', label: 'Overview' },
    { to: '/race-log', label: 'Race Log' },
    { to: '/skills', label: 'Skills' },
    { to: '/improve', label: 'Improve' },
  ];

  return (
    <nav className="bg-bg-dark sticky top-0 z-50">
      <div className="container">
        <div className="flex items-center justify-between py-4">
          {/* Navigation Tabs */}
          <div className="flex gap-6">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `font-semibold text-base transition-all py-2 ${
                    isActive
                      ? 'text-text-inverse border-b-2 border-primary'
                      : 'text-text-secondary hover:text-text-inverse'
                  }`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </div>

          {/* Driver Selector */}
          <DriverSelector
            value={selectedDriver}
            onChange={handleDriverChange}
            drivers={drivers}
          />
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
