import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useDriver } from '../../context/DriverContext';
import './DashboardTabs.css';

/**
 * DashboardTabs - Unified navigation tabs for all dashboard pages
 *
 * Features:
 * - Scout-aware route switching (automatically uses /scout/driver/:num/* when from scout)
 * - Active tab highlighting
 * - Consistent styling across all pages
 * - Full width below header
 */
export default function DashboardTabs() {
  const { selectedDriverNumber } = useDriver();
  const location = useLocation();

  // Detect scout context
  const isFromScout = location.pathname.startsWith('/scout/driver/');

  return (
    <div className="dashboard-nav-tabs-container">
      <div className="dashboard-nav-tabs">
        <NavLink
          to={isFromScout ? `/scout/driver/${selectedDriverNumber}/overview` : "/overview"}
          className={({ isActive }) => `dashboard-tab ${isActive ? 'active' : ''}`}
        >
          Overview
        </NavLink>
        <NavLink
          to={isFromScout ? `/scout/driver/${selectedDriverNumber}/race-log` : "/race-log"}
          className={({ isActive }) => `dashboard-tab ${isActive ? 'active' : ''}`}
        >
          Race Log
        </NavLink>
        <NavLink
          to={isFromScout ? `/scout/driver/${selectedDriverNumber}/skills` : "/skills"}
          className={({ isActive }) => `dashboard-tab ${isActive ? 'active' : ''}`}
        >
          Skills
        </NavLink>
        <NavLink
          to={isFromScout ? `/scout/driver/${selectedDriverNumber}/improve` : "/improve"}
          className={({ isActive }) => `dashboard-tab ${isActive ? 'active' : ''}`}
        >
          Improve
        </NavLink>
      </div>
    </div>
  );
}
