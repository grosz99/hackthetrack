/**
 * RoleContext - Global state for user role (Driver vs Coach)
 * Provides role-aware personalization across the platform
 */

import { createContext, useContext, useState, useEffect } from 'react';
import PropTypes from 'prop-types';

const RoleContext = createContext();

export const RoleProvider = ({ children }) => {
  const [userRole, setUserRole] = useState(
    localStorage.getItem('httt_user_role') || null
  );

  const [showRoleBanner, setShowRoleBanner] = useState(
    userRole && !localStorage.getItem('httt_role_banner_dismissed')
  );

  const updateRole = (role) => {
    localStorage.setItem('httt_user_role', role);
    setUserRole(role);
    // Re-show banner when role changes
    localStorage.removeItem('httt_role_banner_dismissed');
    setShowRoleBanner(true);
  };

  const dismissBanner = () => {
    localStorage.setItem('httt_role_banner_dismissed', 'true');
    setShowRoleBanner(false);
  };

  return (
    <RoleContext.Provider value={{
      userRole,
      updateRole,
      showRoleBanner,
      dismissBanner
    }}>
      {children}
    </RoleContext.Provider>
  );
};

RoleProvider.propTypes = {
  children: PropTypes.node.isRequired
};

export const useRole = () => {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error('useRole must be used within RoleProvider');
  }
  return context;
};
