/**
 * RoleGuidanceBanner - Contextual tips for Drivers vs Coaches
 * Shows role-specific guidance on how to use the Rankings page
 */

import PropTypes from 'prop-types';
import { useRole } from '../../context/RoleContext';
import './RoleGuidanceBanner.css';

const ROLE_CONTENT = {
  driver: {
    icon: '🏎️',
    badge: 'DRIVER',
    title: 'Driver Performance View',
    tips: (
      <>
        Start by finding drivers who excel where you struggle - they're your benchmarks.
        Click on <strong>top performers in specific factors</strong> (Speed, Consistency, etc.) to study their techniques.
        Look for drivers with similar Overall Scores but different factor distributions - what can you learn from them?
      </>
    ),
    switchTo: 'Coach'
  },
  coach: {
    icon: '📋',
    badge: 'COACH',
    title: 'Coach Evaluation View',
    tips: (
      <>
        Compare your athletes against the field - where do they stand in each factor?
        <strong>Identify talent gaps:</strong> Which factors need the most development work?
        Use comparative analysis to find training opportunities and create evidence-based development plans for your team.
      </>
    ),
    switchTo: 'Driver'
  }
};

export default function RoleGuidanceBanner() {
  const { userRole, updateRole, showRoleBanner, dismissBanner } = useRole();

  if (!userRole || !showRoleBanner) {
    return null;
  }

  const content = ROLE_CONTENT[userRole];

  const handleRoleSwitch = () => {
    const newRole = userRole === 'driver' ? 'coach' : 'driver';
    updateRole(newRole);
  };

  return (
    <div className="role-guidance-banner">
      <button
        className="banner-dismiss-btn"
        onClick={dismissBanner}
        aria-label="Dismiss guidance banner"
      >
        ✕
      </button>

      <div className="role-guidance-icon">
        <span className="role-icon-emoji">{content.icon}</span>
      </div>

      <div className="role-guidance-content">
        <div className="role-guidance-header">
          <span className="role-badge">{content.badge}</span>
          <h3 className="role-guidance-title">{content.title}</h3>
        </div>
        <p className="role-guidance-tips">{content.tips}</p>
      </div>

      <button
        className="role-toggle-btn"
        onClick={handleRoleSwitch}
        aria-label={`Switch to ${content.switchTo} view`}
      >
        Switch to {content.switchTo} View
      </button>
    </div>
  );
}

RoleGuidanceBanner.propTypes = {};
