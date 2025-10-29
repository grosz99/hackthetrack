import { NavLink } from 'react-router-dom';
import './Navigation.css';

function Navigation() {
  return (
    <nav className="main-nav">
      <div className="nav-brand">
        <div className="gr-logo">GR</div>
        <span className="brand-text">Racing Analytics</span>
      </div>

      <div className="nav-links">
        <NavLink
          to="/track-intelligence"
          className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
        >
          Track Intelligence
        </NavLink>
        <NavLink
          to="/strategy"
          className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
        >
          AI Strategy Coach
        </NavLink>
        <NavLink
          to="/telemetry"
          className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
        >
          Telemetry Comparison
        </NavLink>
      </div>

      <div className="nav-subtitle">
        Making the Predictable Unpredictable
      </div>
    </nav>
  );
}

export default Navigation;
