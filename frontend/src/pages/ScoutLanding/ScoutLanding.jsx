import { useState, useEffect } from 'react';
import { useDriver } from '../../context/DriverContext';
import { useScout } from '../../context/ScoutContext';
import { applyFilters, sortDrivers } from '../../utils/classification';
import FilterSidebar from '../../components/FilterSidebar/FilterSidebar';
import DriverCard from '../../components/DriverCard/DriverCard';
import './ScoutLanding.css';

export default function ScoutLanding() {
  const { drivers } = useDriver();
  const { filters, sortBy, setSortBy, sortOrder, setSortOrder, updateFilter } = useScout();
  const [filteredDrivers, setFilteredDrivers] = useState([]);

  // Apply filters and sorting whenever they change
  useEffect(() => {
    let result = applyFilters(drivers, filters);
    result = sortDrivers(result, sortBy, sortOrder);
    setFilteredDrivers(result);
  }, [drivers, filters, sortBy, sortOrder]);

  const toggleSortOrder = () => {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
  };

  return (
    <div className="scout-landing">
      {/* Header */}
      <div className="scout-header">
        <div className="header-content">
          <h1 className="scout-title">Scout Portal</h1>
          <p className="scout-subtitle">Driver Talent Evaluation & Recruitment</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="scout-content">
        {/* Filter Sidebar */}
        <FilterSidebar resultCount={filteredDrivers.length} />

        {/* Driver Grid */}
        <div className="driver-grid-container">
          {/* Grid Controls */}
          <div className="grid-controls">
            <div className="controls-left">
              <input
                type="text"
                placeholder="Search by name or number..."
                value={filters.searchQuery}
                onChange={(e) => updateFilter('searchQuery', e.target.value)}
                className="search-input"
              />
            </div>

            <div className="controls-right">
              <label className="sort-label">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="sort-select"
              >
                <option value="overall_score">Overall Score</option>
                <option value="speed">Speed</option>
                <option value="consistency">Consistency</option>
                <option value="avg_finish">Avg Finish</option>
                <option value="races">Experience</option>
                <option value="number">Driver Number</option>
              </select>

              <button
                onClick={toggleSortOrder}
                className="sort-order-btn"
                title={sortOrder === 'desc' ? 'Descending' : 'Ascending'}
              >
                {sortOrder === 'desc' ? '↓' : '↑'}
              </button>
            </div>
          </div>

          {/* Driver Grid */}
          {filteredDrivers.length > 0 ? (
            <div className="driver-grid">
              {filteredDrivers.map(driver => (
                <DriverCard key={driver.number} driver={driver} />
              ))}
            </div>
          ) : (
            <div className="no-results">
              <div className="no-results-icon">🔍</div>
              <h3>No drivers found</h3>
              <p>Try adjusting your filters</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
