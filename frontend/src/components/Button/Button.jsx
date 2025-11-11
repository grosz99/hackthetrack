/**
 * Button Component - Unified button styles
 * Racing-inspired design with consistent sizing and colors
 */

import PropTypes from 'prop-types';
import { NavLink } from 'react-router-dom';
import './Button.css';

export default function Button({
  children,
  variant = 'primary',
  size = 'medium',
  to,
  href,
  onClick,
  disabled = false,
  fullWidth = false,
  icon,
  className = '',
  ...props
}) {
  const baseClasses = `button button-${variant} button-${size}`;
  const widthClass = fullWidth ? 'button-full-width' : '';
  const classes = `${baseClasses} ${widthClass} ${className}`.trim();

  // Link button (internal navigation)
  if (to && !disabled) {
    return (
      <NavLink
        to={to}
        className={classes}
        {...props}
      >
        {icon && <span className="button-icon">{icon}</span>}
        <span>{children}</span>
      </NavLink>
    );
  }

  // Anchor button (external links)
  if (href && !disabled) {
    return (
      <a
        href={href}
        className={classes}
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {icon && <span className="button-icon">{icon}</span>}
        <span>{children}</span>
      </a>
    );
  }

  // Regular button
  return (
    <button
      className={classes}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {icon && <span className="button-icon">{icon}</span>}
      <span>{children}</span>
    </button>
  );
}

Button.propTypes = {
  children: PropTypes.node.isRequired,
  variant: PropTypes.oneOf(['primary', 'secondary', 'outline', 'ghost', 'danger']),
  size: PropTypes.oneOf(['small', 'medium', 'large']),
  to: PropTypes.string,
  href: PropTypes.string,
  onClick: PropTypes.func,
  disabled: PropTypes.bool,
  fullWidth: PropTypes.bool,
  icon: PropTypes.node,
  className: PropTypes.string,
};
