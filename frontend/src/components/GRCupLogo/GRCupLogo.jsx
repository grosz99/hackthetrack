/**
 * GR Cup North America Logo Component
 * Replicates the official Toyota Gazoo Racing GR Cup branding
 */

import './GRCupLogo.css';

export default function GRCupLogo({ size = 'medium' }) {
  return (
    <div className={`gr-cup-logo gr-cup-logo-${size}`}>
      <div className="gr-cup-container">
        <div className="gr-cup-top">
          <span className="toyota-text">TOYOTA GAZOO </span>
          <span className="racing-text">Racing</span>
        </div>
        <div className="gr-cup-main">
          <span className="gr-text">G</span>
          <span className="r-text">R</span>
          <span className="cup-text"> CUP</span>
        </div>
        <div className="gr-cup-bottom">
          <span className="region-text">NORTH AMERICA</span>
        </div>
      </div>
    </div>
  );
}
