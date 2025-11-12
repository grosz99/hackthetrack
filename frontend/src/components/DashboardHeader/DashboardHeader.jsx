import { useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useDriver } from '../../context/DriverContext';
import { useScout } from '../../context/ScoutContext';
import { classifyDriver } from '../../utils/classification';
import ClassificationBadge from '../ClassificationBadge/ClassificationBadge';
import './DashboardHeader.css';

/**
 * DashboardHeader - Unified header component for all dashboard pages
 *
 * Features:
 * - Circular driver number badge
 * - Driver selector with all 34 drivers from DriverContext
 * - Scout breadcrumb when navigated from scout portal
 * - Classification badge display when from scout
 * - Consistent Toyota racing theme
 */
export default function DashboardHeader({ driverData, pageName }) {
  const { selectedDriverNumber, setSelectedDriverNumber, drivers } = useDriver();
  const { driverNumber: routeDriverNumber } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  // Detect scout context
  const isFromScout = location.pathname.startsWith('/scout/driver/');
  const classification = driverData ? classifyDriver(driverData) : null;

  // Sync route params with DriverContext
  useEffect(() => {
    if (routeDriverNumber) {
      const driverNum = Number(routeDriverNumber);
      if (driverNum !== selectedDriverNumber) {
        setSelectedDriverNumber(driverNum);
      }
    }
  }, [routeDriverNumber, selectedDriverNumber, setSelectedDriverNumber]);

  // Handle driver change - update context AND navigate
  const handleDriverChange = (newDriverNumber) => {
    setSelectedDriverNumber(newDriverNumber);

    // Determine current page from pathname
    const currentPage = location.pathname.split('/').pop();
    const validPages = ['overview', 'race-log', 'skills', 'improve'];
    const page = validPages.includes(currentPage) ? currentPage : 'overview';

    // Navigate to same page with new driver
    navigate(`/driver/${newDriverNumber}/${page}`);
  };

  return (
    <>
      {/* Breadcrumb Navigation */}
      {isFromScout ? (
        /* Scout Breadcrumb - Show when navigated from scout */
        <div className="scout-breadcrumb">
          <button
            onClick={() => navigate('/scout')}
            className="back-to-scout-btn"
          >
            <span className="arrow">←</span>
            <span>Back to Scout Portal</span>
          </button>
          <div className="breadcrumb-trail">
            <span className="trail-scout">Scout Portal</span>
            <span className="trail-separator">›</span>
            <span className="trail-driver">Driver #{selectedDriverNumber}</span>
            <span className="trail-separator">›</span>
            <span className="trail-page">{pageName}</span>
          </div>
        </div>
      ) : (
        /* Rankings Breadcrumb - Show when navigated from rankings */
        <div className="scout-breadcrumb">
          <button
            onClick={() => navigate('/rankings')}
            className="back-to-scout-btn"
          >
            <span className="arrow">←</span>
            <span>Back to Rankings</span>
          </button>
          <div className="breadcrumb-trail">
            <span className="trail-scout">Rankings</span>
            <span className="trail-separator">›</span>
            <span className="trail-driver">Driver #{selectedDriverNumber}</span>
            <span className="trail-separator">›</span>
            <span className="trail-page">{pageName}</span>
          </div>
        </div>
      )}

      {/* Header Section */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="driver-number-display">
            <span className="number-large">{selectedDriverNumber}</span>
          </div>
          <div className="driver-name-section">
            <div className="driver-name-row">
              <h1 className="driver-name">Driver #{selectedDriverNumber}</h1>
              {isFromScout && classification && (
                <ClassificationBadge classification={classification} size="large" />
              )}
            </div>
            <div className="season-subtitle">Toyota Gazoo Series</div>
          </div>

          {/* Driver Selector */}
          <div className="driver-selector-container">
            <span className="selector-label">Select Driver</span>
            <select
              value={selectedDriverNumber}
              onChange={(e) => handleDriverChange(Number(e.target.value))}
              className="driver-selector"
            >
              {drivers.map((driver) => (
                <option key={driver.number} value={driver.number}>
                  {driver.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </>
  );
}
