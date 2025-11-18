import { useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { useDriver } from '../../context/DriverContext';
import { useScout } from '../../context/ScoutContext';
import { classifyDriver } from '../../utils/classification';
import ClassificationBadge from '../ClassificationBadge/ClassificationBadge';
import GibbsAIBranding from '../GibbsAIBranding/GibbsAIBranding';
import './DashboardHeader.css';

/**
 * Get page-specific description text
 */
const getPageDescription = (pageName) => {
  const descriptions = {
    'Overview': 'View comprehensive performance metrics, 4-factor analysis breakdown, and AI-powered insights into driver strengths and development areas',
    'Race Log': 'Explore complete race history with detailed lap-by-lap analysis, position changes, and performance trends across all championship rounds',
    'Skills': 'Dive deep into the 4-factor performance model analyzing speed, consistency, racecraft, and tire management with statistical breakdowns',
    'Improve': 'Access personalized AI coaching recommendations, practice plans, and data-driven improvement strategies tailored to driver performance gaps'
  };

  return descriptions[pageName] || 'Explore detailed driver performance analytics and AI-powered insights';
};

/**
 * DashboardHeader - Unified header component with Gibbs AI branding
 *
 * Features:
 * - Prominent Gibbs AI for Toyota Gazoo Racing branding
 * - Sticky header that stays visible on scroll
 * - Circular driver number badge (reduced size)
 * - Driver selector with all 34 drivers from DriverContext
 * - Scout/Rankings breadcrumb navigation
 * - Classification badge display when from scout
 * - Consistent TGR theme
 * - Contextual page descriptions
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

      {/* Header Section - Sticky with consistent Rankings flow */}
      <div className="dashboard-header">
        <div className="header-content">
          {/* LEFT: Driver Section (40%) - Matches Rankings icon+title layout */}
          <div className="driver-section">
            <div className="driver-badge-large">
              <span className="badge-number">{selectedDriverNumber}</span>
            </div>
            <div className="driver-info-stack">
              <h1 className="driver-name-large">Driver #{selectedDriverNumber}</h1>
              {isFromScout && classification && (
                <ClassificationBadge classification={classification} size="medium" />
              )}
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

          {/* CENTER: Spacer (20%) */}
          <div className="header-spacer"></div>

          {/* RIGHT: Gibbs AI Branding (40%) - Matches Rankings logo position */}
          <div className="brand-section-right">
            <GibbsAIBranding size="large" />
          </div>
        </div>

        {/* Description Section - Contextual page information */}
        <div className="header-description">
          <p className="description-text">
            {getPageDescription(pageName)}
          </p>
        </div>
      </div>
    </>
  );
}
