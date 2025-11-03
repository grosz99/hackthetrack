import React from 'react';
/**
 * DriverSelector - Dropdown for selecting drivers
 *
 * PFF-style dropdown with search functionality
 */

import { useState, useEffect } from 'react';
import PercentileBadge from './PercentileBadge';

export default function DriverSelector({ value, onChange, drivers = [], className = '' }) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Get current driver
  const currentDriver = drivers.find(d => d.driver_number === parseInt(value)) || drivers[0];

  // Filter drivers by search term
  const filteredDrivers = drivers.filter(driver =>
    driver.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    driver.driver_number?.toString().includes(searchTerm)
  );

  // Handle driver selection
  const handleSelect = (driverNumber) => {
    onChange(driverNumber);
    setIsOpen(false);
    setSearchTerm('');
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (isOpen && !e.target.closest('.driver-selector')) {
        setIsOpen(false);
        setSearchTerm('');
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [isOpen]);

  if (!currentDriver) return null;

  return (
    <div className={`driver-selector relative ${className}`}>
      {/* Selected Driver Display */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 px-4 py-2 bg-bg-darker border border-border-darker rounded-lg hover:border-primary transition-all min-w-[280px]"
      >
        <span className="font-mono text-lg font-bold text-primary">
          #{currentDriver.driver_number}
        </span>
        <div className="flex-1 text-left">
          <div className="font-semibold text-text-inverse">
            {currentDriver.name || `Driver #${currentDriver.driver_number}`}
          </div>
          {currentDriver.overall_rating && (
            <div className="text-xs text-text-secondary">
              {currentDriver.overall_rating}/100 - {currentDriver.grade}
            </div>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-text-secondary transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full mt-2 w-full bg-bg-primary border border-border rounded-lg shadow-xl z-50 max-h-[400px] overflow-hidden">
          {/* Search Box */}
          <div className="p-3 border-b border-border">
            <input
              type="text"
              placeholder="Search driver..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 bg-bg-tertiary border border-border rounded text-text-primary placeholder-text-muted focus:outline-none focus:border-primary"
              autoFocus
            />
          </div>

          {/* Driver List */}
          <div className="overflow-y-auto max-h-[320px]">
            {filteredDrivers.length === 0 ? (
              <div className="px-4 py-8 text-center text-text-muted">
                No drivers found
              </div>
            ) : (
              filteredDrivers.map((driver) => (
                <button
                  key={driver.driver_number}
                  onClick={() => handleSelect(driver.driver_number)}
                  className={`w-full flex items-center gap-3 px-4 py-3 hover:bg-bg-secondary transition-colors text-left ${
                    driver.driver_number === currentDriver.driver_number ? 'bg-bg-secondary' : ''
                  }`}
                >
                  <span className="font-mono font-bold text-primary">
                    #{driver.driver_number}
                  </span>
                  <div className="flex-1">
                    <div className="font-semibold text-text-primary">
                      {driver.name || `Driver #${driver.driver_number}`}
                    </div>
                    {driver.team && (
                      <div className="text-xs text-text-secondary">
                        {driver.team}
                      </div>
                    )}
                  </div>
                  {driver.overall_rating && (
                    <div className="text-sm font-mono text-text-secondary">
                      {driver.overall_rating}
                    </div>
                  )}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
