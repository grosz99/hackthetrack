import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import GibbsAIBranding from '../GibbsAIBranding/GibbsAIBranding';
import './WelcomeModal.css';

export default function WelcomeModal({ onClose }) {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      id: 'welcome',
      title: 'Decode Performance. Dominate the Track.',
      subtitle: 'AI-Powered Driver Development',
      content: (
        <div className="welcome-intro">
          <div className="welcome-logo">
            <GibbsAIBranding size="large" />
          </div>
          <p className="intro-text">
            Welcome to Gibbs AI. Our platform uses a validated <strong>4-Factor Performance Model</strong> combined with Claude AI to provide data-driven insights and personalized coaching for driver development.
          </p>
          <p className="intro-subtext">
            The perfect blend of statistical analysis and AI-powered scouting to help identify and develop the drivers of the future.
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
    {
      id: 'four-factors',
      title: 'The 4-Factor Performance Model',
      content: (
        <div className="four-factors-section">
          <div className="factor-overview">
            <p>
              Our AI analyzes driver performance across four validated dimensions (R²=0.895).
            </p>
          </div>

          <div className="factor-definitions-grid">
            <div className="factor-card-uniform">
              <h4>Speed (46.6%)</h4>
              <p>Raw pace through lap times and sector performance showing pure driving ability.</p>
            </div>
            <div className="factor-card-uniform">
              <h4>Consistency (29.1%)</h4>
              <p>Lap-to-lap repeatability indicating better control and predictable performance.</p>
            </div>
            <div className="factor-card-uniform">
              <h4>Racecraft (14.9%)</h4>
              <p>Wheel-to-wheel racing skills including overtaking efficiency and positioning.</p>
            </div>
            <div className="factor-card-uniform">
              <h4>Tire Management (9.5%)</h4>
              <p>Ability to preserve tire performance throughout a stint while staying competitive.</p>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'platform-features',
      title: 'Platform Features',
      content: (
        <div className="features-grid">
          <div className="feature-tile">
            <h4>Overview</h4>
            <p>Season statistics, 4-factor radar chart, and race-by-race performance analysis</p>
          </div>
          <div className="feature-tile">
            <h4>Skills</h4>
            <p>Detailed factor breakdowns with underlying metrics and peer comparisons</p>
          </div>
          <div className="feature-tile">
            <h4>Race Log</h4>
            <p>Complete race history with lap times, positions, and performance trends</p>
          </div>
          <div className="feature-tile">
            <h4>AI Coach</h4>
            <p>Claude-powered insights, practice plans, and personalized improvement recommendations</p>
          </div>
        </div>
      )
    }
  ];

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
