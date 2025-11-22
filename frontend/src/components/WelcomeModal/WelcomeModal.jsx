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
    // Auto-advance to next slide after selecting role
    setTimeout(() => {
      setCurrentSlide(1);
    }, 300);
  };

  // Build slides dynamically based on selected role
  const getSlides = () => {
    // Slide 1: Welcome with role selection (same for everyone)
    const welcomeSlide = {
      id: 'welcome',
      title: 'Welcome to Gibbs AI',
      subtitle: 'Choose your role to unlock AI-powered performance insights',
      content: (
        <div className="role-selection-section">
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
                <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  {/* Outer rim with flat bottom */}
                  <path d="M4 12 A8 8 0 0 1 20 12"></path>
                  <path d="M4 12 L6 15 L18 15 L20 12"></path>
                  {/* Center hub */}
                  <circle cx="12" cy="12" r="2.5"></circle>
                  {/* Three spokes */}
                  <line x1="12" y1="4" x2="12" y2="9.5"></line>
                  <line x1="5.5" y1="9.5" x2="10" y2="11"></line>
                  <line x1="18.5" y1="9.5" x2="14" y2="11"></line>
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
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                  <line x1="9" y1="9" x2="15" y2="9"></line>
                  <line x1="9" y1="15" x2="15" y2="15"></line>
                  <line x1="9" y1="12" x2="12" y2="12"></line>
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
    };

    // Slide 2: Why Gibbs AI (same for everyone)
    const whyGibbsSlide = {
      id: 'why-gibbs',
      title: 'Why Gibbs AI?',
      content: (
        <div className="gibbs-story-section">
          <div className="welcome-logo">
            <ToyotaGibbsLogo size="large" />
          </div>
          <div className="gibbs-story">
            <p className="story-intro">
              <strong>Joe Gibbs</strong> is a legendary figure in American motorsports and football—a Hall of Fame NFL coach who won three Super Bowls with the Washington Redskins and a Toyota partner who built one of NASCAR's most successful racing organizations.
            </p>
            <p className="story-intro">
              Joe Gibbs Racing has developed and championed some of the winningest drivers of the 21st century, including <strong>Tony Stewart</strong>, <strong>Joey Logano</strong>, and <strong>Denny Hamlin</strong>. His ability to identify raw talent, provide world-class development programs, and create championship-winning teams is unmatched across both motorsports and professional football. As a long-time Toyota partner in NASCAR, Joe Gibbs Racing has been instrumental in Toyota's success in American racing, combining technical excellence with driver development.
            </p>
          </div>
        </div>
      )
    };

    // Driver-specific slides (3-4)
    const driverSlide1 = {
      id: 'driver-performance',
      title: 'Track Your Performance',
      content: (
        <div className="features-grid">
          <div className="feature-tile">
            <h4>Performance Dashboard</h4>
            <p>View your season statistics, 4-factor radar chart, and race-by-race performance analysis to understand your strengths.</p>
          </div>
          <div className="feature-tile">
            <h4>Race Log</h4>
            <p>Track your progress over time with complete race history, lap times, and performance trends across the season.</p>
          </div>
          <div className="feature-tile">
            <h4>Rankings</h4>
            <p>See where you stand against other drivers. Find benchmarks and study top performers in areas where you want to improve.</p>
          </div>
          <div className="feature-tile">
            <h4>Driver Development</h4>
            <p>Get personalized practice recommendations based on your weakest factors. Understand exactly what skills to work on to maximize your lap time improvements.</p>
          </div>
        </div>
      )
    };

    const driverSlide2 = {
      id: 'driver-development',
      title: 'Get Faster with Validated AI Insights',
      content: (
        <div className="features-flow">
          <div className="feature-tile">
            <h4>Proven Performance Prediction (R²=0.895)</h4>
            <p>Our 4-Factor Model explains 89.5% of race performance variation—validated across thousands of laps. When you improve your weakest factor, you WILL see measurable lap time gains. This isn't guesswork, it's data science.</p>
          </div>
          <div className="feature-tile">
            <h4>Focus on What Actually Makes You Faster</h4>
            <p>Stop wasting practice time on random drills. Our AI identifies your biggest performance limiters across Speed (46.6%), Consistency (29.1%), Racecraft (14.9%), and Tire Management (9.5%). Target your weakest link for maximum improvement.</p>
          </div>
          <div className="feature-tile">
            <h4>Personalized Path to Podiums</h4>
            <p>Get specific, actionable recommendations tailored to YOUR performance gaps. Whether you need to work on qualifying pace, reduce lap time variance, improve overtaking, or extend tire life—you'll know exactly what to practice and why it matters.</p>
          </div>
        </div>
      )
    };

    // Coach-specific slides (3-4)
    const coachSlide1 = {
      id: 'coach-4-factors',
      title: 'The 4-Factor Performance Model',
      content: (
        <div className="four-factors-section">
          <div className="factor-overview" style={{ display: 'block' }}>
            <p>
              Our AI analyzes driver performance across four validated dimensions (R²=0.895). Use this model to objectively assess athlete strengths and weaknesses.
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
    };

    const coachSlide2 = {
      id: 'coach-development',
      title: 'Build Championship-Winning Drivers',
      content: (
        <div className="features-flow">
          <div className="feature-tile">
            <h4>Identify High-Impact Development Areas</h4>
            <p>Pinpoint exactly which of the 4 factors will yield the biggest performance gains for each athlete. Focus coaching efforts where they matter most—speed deficits, consistency issues, racecraft gaps, or tire management weaknesses.</p>
          </div>
          <div className="feature-tile">
            <h4>Track Measurable Progress</h4>
            <p>Monitor athlete improvement over time with objective metrics. See how your coaching interventions impact Speed, Consistency, Racecraft, and Tire Management scores across race weekends and seasons.</p>
          </div>
          <div className="feature-tile">
            <h4>Build Data-Driven Development Plans</h4>
            <p>Create personalized training programs backed by AI analysis. Target specific weaknesses with evidence-based recommendations that accelerate driver development and close performance gaps.</p>
          </div>
        </div>
      )
    };

    // Return appropriate slides based on selected role
    if (selectedRole === 'driver') {
      return [welcomeSlide, whyGibbsSlide, driverSlide1, driverSlide2];
    } else if (selectedRole === 'coach') {
      return [welcomeSlide, whyGibbsSlide, coachSlide1, coachSlide2];
    } else {
      // No role selected yet, just show welcome slide
      return [welcomeSlide, whyGibbsSlide];
    }
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
              {currentSlide !== 0 && (
                <button className="btn-next" onClick={handleNext}>
                  {currentSlide < slides.length - 1 ? 'Next' : 'Get Started'}
                </button>
              )}
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
