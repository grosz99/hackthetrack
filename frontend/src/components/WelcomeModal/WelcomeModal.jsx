import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import PropTypes from 'prop-types';
import { useRole } from '../../context/RoleContext';
import ToyotaGibbsLogo from '../ToyotaGibbsLogo/ToyotaGibbsLogo';
import './WelcomeModal.css';

export default function WelcomeModal({ onClose }) {
  const { userRole, updateRole } = useRole();
  const [currentSlide, setCurrentSlide] = useState(0);
  const [selectedRole, setSelectedRole] = useState(userRole);

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
    updateRole(role);
  };

  // Build slides dynamically based on selected role
  const getSlides = () => {
    const baseSlides = [
    {
      id: 'welcome',
      title: 'Decode Performance. Dominate the Track.',
      subtitle: 'AI-Powered Driver Development',
      content: (
        <div className="welcome-intro">
          <div className="welcome-logo">
            <ToyotaGibbsLogo size="large" />
          </div>
          <p className="intro-text">
            Welcome to Gibbs AI. Our platform uses a validated <strong>4-Factor Performance Model</strong> and live AI feeds to personalize coaching needs for driver development.
          </p>
        </div>
      )
    },
    {
      id: 'role-selection',
      title: 'Personalize Your Experience',
      content: (
        <div className="role-selection-section">
          <div className="role-selection-intro">
            <h3>Help us customize your journey...</h3>
            <p>Are you using this platform as a driver looking to improve, or as a coach evaluating athletes?</p>
          </div>

          <div className="role-cards-container">
            <div
              className={`role-card ${selectedRole === 'driver' ? 'selected' : ''}`}
              onClick={() => handleRoleSelect('driver')}
              role="button"
              tabIndex="0"
              aria-label="Select Driver role"
              aria-pressed={selectedRole === 'driver'}
              onKeyPress={(e) => { if (e.key === 'Enter' || e.key === ' ') handleRoleSelect('driver'); }}
            >
              <div className="role-icon-wrapper">
                <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M12 2v20M2 12h20"></path>
                </svg>
              </div>
              <h4>DRIVER</h4>
              <p>I'm looking to improve my performance</p>
              <ul className="role-benefits">
                <li>Personal improvement tracking</li>
                <li>Benchmark against top drivers</li>
                <li>Identify skill gaps</li>
                <li>Actionable practice recommendations</li>
              </ul>
            </div>

            <div
              className={`role-card ${selectedRole === 'coach' ? 'selected' : ''}`}
              onClick={() => handleRoleSelect('coach')}
              role="button"
              tabIndex="0"
              aria-label="Select Coach role"
              aria-pressed={selectedRole === 'coach'}
              onKeyPress={(e) => { if (e.key === 'Enter' || e.key === ' ') handleRoleSelect('coach'); }}
            >
              <div className="role-icon-wrapper">
                <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M9 5H2v14h7M15 5h7v14h-7M9 5v14M15 5v14"></path>
                  <path d="M9 12h6"></path>
                </svg>
              </div>
              <h4>COACH</h4>
              <p>I'm coaching & evaluating athletes</p>
              <ul className="role-benefits">
                <li>Athlete evaluation tools</li>
                <li>Development planning insights</li>
                <li>Comparative performance analysis</li>
                <li>Team-wide skill assessments</li>
              </ul>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'welcome',
      title: 'Decode Performance. Dominate the Track.',
      subtitle: 'AI-Powered Driver Development',
      content: (
        <div className="welcome-intro">
          <div className="welcome-logo">
            <ToyotaGibbsLogo size="large" />
          </div>
          <p className="intro-text">
            Welcome to Gibbs AI. Our platform uses a validated <strong>4-Factor Performance Model</strong> and live AI feeds to personalize coaching needs for driver development.
          </p>
        </div>
      )
    },
    {
      id: 'why-gibbs',
      title: 'Why Gibbs AI?',
      content: (
        <div className="gibbs-story-section">
          <div className="gibbs-story">
            <p className="story-intro">
              <strong>Joe Gibbs</strong> is a legendary figure in American motorsports and football—a Hall of Fame NFL coach who won three Super Bowls with the Washington Redskins and a Toyota partner who built one of NASCAR's most successful racing organizations.
            </p>

            <div className="accomplishments-grid">
              <div className="accomplishment">
                <h4>NASCAR Excellence</h4>
                <p>Joe Gibbs Racing has developed and championed some of the winningest drivers of the 21st century, including <strong>Tony Stewart</strong>, <strong>Joey Logano</strong>, and <strong>Denny Hamlin</strong>.</p>
              </div>

              <div className="accomplishment">
                <h4>Talent Development</h4>
                <p>His ability to identify raw talent, provide world-class development programs, and create championship-winning teams is unmatched across both motorsports and professional football.</p>
              </div>

              <div className="accomplishment">
                <h4>Toyota Partnership</h4>
                <p>As a long-time Toyota partner in NASCAR, Joe Gibbs Racing has been instrumental in Toyota's success in American racing, combining technical excellence with driver development.</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    ];

    // Role-specific slide for 4 Factors
    const fourFactorsSlide = {
      id: 'four-factors',
      title: 'The 4-Factor Performance Model',
      content: (
        <div className="four-factors-section">
          <div className="factor-overview">
            <p>
              Our AI analyzes driver performance across four validated dimensions (R²=0.895).
              {selectedRole === 'driver' && <strong> Identify which factor needs the most improvement.</strong>}
              {selectedRole === 'coach' && <strong> Use this validated model to objectively assess athlete strengths and weaknesses.</strong>}
            </p>
          </div>

          <div className="factor-definitions-grid">
            <div className="factor-card-uniform">
              <h4>Speed (46.6%)</h4>
              <p>Raw pace through lap times and sector performance showing pure driving ability.</p>
              <div className="factor-variables">
                <span className="variable-label">Variables:</span>
                <span className="variable-tag">Avg Lap Time</span>
                <span className="variable-tag">Best Lap</span>
                <span className="variable-tag">Sector Times</span>
              </div>
            </div>
            <div className="factor-card-uniform">
              <h4>Consistency (29.1%)</h4>
              <p>Lap-to-lap repeatability indicating better control and predictable performance.</p>
              <div className="factor-variables">
                <span className="variable-label">Variables:</span>
                <span className="variable-tag">Lap Time Std Dev</span>
                <span className="variable-tag">Clean Laps %</span>
                <span className="variable-tag">DNF Rate</span>
              </div>
            </div>
            <div className="factor-card-uniform">
              <h4>Racecraft (14.9%)</h4>
              <p>Wheel-to-wheel racing skills including overtaking efficiency and positioning.</p>
              <div className="factor-variables">
                <span className="variable-label">Variables:</span>
                <span className="variable-tag">Passes Made</span>
                <span className="variable-tag">Positions Gained</span>
                <span className="variable-tag">Start Performance</span>
              </div>
            </div>
            <div className="factor-card-uniform">
              <h4>Tire Management (9.5%)</h4>
              <p>Ability to preserve tire performance throughout a stint while staying competitive.</p>
              <div className="factor-variables">
                <span className="variable-label">Variables:</span>
                <span className="variable-tag">Lap Deg Rate</span>
                <span className="variable-tag">Stint Length</span>
                <span className="variable-tag">Late Pace</span>
              </div>
            </div>
          </div>
        </div>
      )
    },
    };

    // Role-specific slide for Platform Features
    const platformFeaturesSlide = {
      id: 'platform-features',
      title: 'Platform Features',
      content: (
        <div className="features-flow">
          <div className="feature-tile flow-start">
            <h4>Rankings</h4>
            <p>
              {selectedRole === 'driver' && 'Browse all drivers ranked by overall performance. Find benchmarks and study top performers in areas where you want to improve.'}
              {selectedRole === 'coach' && 'Browse all drivers ranked by overall performance. Compare your athletes against the field and identify development opportunities.'}
            </p>
          </div>
          <div className="flow-arrow">↓</div>
          <div className="features-grid-flow">
            <div className="feature-tile">
              <h4>{selectedRole === 'driver' ? 'Your Performance Dashboard' : 'Athlete Overview'}</h4>
              <p>
                {selectedRole === 'driver' && 'Your season statistics, 4-factor radar chart, and race-by-race performance analysis'}
                {selectedRole === 'coach' && 'Complete athlete evaluation: season stats, 4-factor radar chart, and detailed performance analysis'}
              </p>
            </div>
            <div className="feature-tile">
              <h4>Race Log</h4>
              <p>
                {selectedRole === 'driver' && 'Track your progress over time with complete race history, lap times, and performance trends'}
                {selectedRole === 'coach' && 'Performance trend analysis: complete race history with lap times and positions for planning'}
              </p>
            </div>
            <div className="feature-tile">
              <h4>{selectedRole === 'driver' ? 'Skills Breakdown' : 'Coach Skill Review'}</h4>
              <p>
                {selectedRole === 'driver' && 'Identify your development priorities with detailed factor breakdowns and performance gaps'}
                {selectedRole === 'coach' && 'Objective skill assessment tool with detailed factor breakdowns and peer comparisons'}
              </p>
            </div>
            <div className="feature-tile">
              <h4>{selectedRole === 'driver' ? 'Your Development Plan' : 'Coaching Recommendations'}</h4>
              <p>
                {selectedRole === 'driver' && 'AI-powered personalized practice plans and improvement recommendations based on your gaps'}
                {selectedRole === 'coach' && 'Evidence-based coaching recommendations and development planning insights for your athletes'}
              </p>
            </div>
          </div>
        </div>
      )
    };

    return [...baseSlides, fourFactorsSlide, platformFeaturesSlide];
  };

  const slides = getSlides();

  const handleNext = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    } else {
      onClose();
    }
  };

  const handleSkip = () => {
    onClose();
  };

  return (
    <AnimatePresence>
      <motion.div
        className="modal-backdrop"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={handleSkip}
      >
        <motion.div
          className="modal-content"
          initial={{ scale: 0.9, y: 20 }}
          animate={{ scale: 1, y: 0 }}
          exit={{ scale: 0.9, y: 20 }}
          onClick={(e) => e.stopPropagation()}
        >
          <button className="modal-close" onClick={handleSkip} aria-label="Close modal">✕</button>

          <div className="modal-body">
            <AnimatePresence mode="wait">
              <motion.div
                key={slides[currentSlide].id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <h1 className="modal-title">{slides[currentSlide].title}</h1>
                {slides[currentSlide].subtitle && (
                  <p className="modal-subtitle">{slides[currentSlide].subtitle}</p>
                )}
                <div className="modal-slide-content">
                  {slides[currentSlide].content}
                </div>
              </motion.div>
            </AnimatePresence>
          </div>

          <div className="modal-footer">
            <div className="progress-dots">
              {slides.map((_, index) => (
                <button
                  key={index}
                  className={`progress-dot ${index === currentSlide ? 'active' : ''}`}
                  onClick={() => setCurrentSlide(index)}
                  aria-label={`Go to slide ${index + 1}`}
                />
              ))}
            </div>

            <div className="modal-actions">
              <button className="btn-skip" onClick={handleSkip}>
                Skip
              </button>
              <button className="btn-next" onClick={handleNext}>
                {currentSlide < slides.length - 1 ? 'Next' : 'Get Started'}
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

WelcomeModal.propTypes = {
  onClose: PropTypes.func.isRequired
};
