/**
 * GibbsAIBranding Component
 * Primary branding element for Gibbs AI product
 * Displays logo with Toyota Gazoo Racing association
 */

import './GibbsAIBranding.css';
import gibbsLogo from '../../assets/gibbs-ai-logo.png';

export default function GibbsAIBranding({ size = 'large' }) {
  return (
    <div className={`gibbs-branding gibbs-branding-${size}`}>
      <img
        src={gibbsLogo}
        alt="Gibbs AI for Toyota Gazoo Racing"
        className="gibbs-logo"
      />
    </div>
  );
}
