import React from 'react';
import toyotaGibbsLogo from '../../assets/toyota-gibbs-logo.png';
import './ToyotaGibbsLogo.css';

export default function ToyotaGibbsLogo({ size = 'large' }) {
  return (
    <div className={`toyota-gibbs-logo toyota-gibbs-logo-${size}`}>
      <img
        src={toyotaGibbsLogo}
        alt="Toyota Gibbs Racing"
        className="logo-image"
      />
    </div>
  );
}
