import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { TargetIcon, ChartIcon } from '../icons';
import GibbsAIBranding from '../GibbsAIBranding/GibbsAIBranding';
import './WelcomeModal.css';

export default function WelcomeModal({ onClose }) {
  const [currentSlide, setCurrentSlide] = useState(0);

  const slides = [
    {
      id: 'welcome',
      title: 'Decode Performance. Dominate the Track.',
      subtitle: 'Making the Predictable Unpredictable',
      content: (
        <div className="welcome-intro">
          <div className="welcome-logo">
            <GibbsAIBranding size="large" />
          </div>
          <p className="intro-text">
            Welcome to Gibbs AI. The perfect blend of AI and Scouting to help find the drivers of the future.
          </p>
        </div>
      )
    },
    {
      id: 'why-gibbs',
      title: 'Why Gibbs AI?',
      content: (
        <div className="gibbs-story-section">
          <div className="our-mission">
            <h4>Our Mission</h4>
            <p>
              <strong>Gibbs AI</strong> aims to replicate Joe Gibbs' legendary eye for talent and development philosophy. Using validated statistics and AI-powered analysis, we help identify and develop the drivers of the future—just as Joe Gibbs has done for decades in NASCAR and the NFL.
            </p>
          </div>

          <div className="gibbs-hero">
            <div className="gibbs-icon">
              <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
                <circle cx="40" cy="40" r="38" fill="#EB0A1E" stroke="#B80818" strokeWidth="4"/>
                <path d="M40 20L48 36L64 38L52 50L55 66L40 58L25 66L28 50L16 38L32 36L40 20Z" fill="#FFD700" stroke="#B8860B" strokeWidth="2"/>
              </svg>
            </div>
            <h3>An Eye for Talent</h3>
          </div>

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
      id: 'three-pillars',
      title: 'Three Pillars of Performance',
      content: (
        <div className="pillars-grid">
          <div className="pillar">
            <TargetIcon size="lg" />
            <h3>Performance Intelligence</h3>
            <p className="pillar-subtitle">4-Factor Statistical Model (R²=0.895)</p>
            <ul className="feature-list">
              <li><strong>Speed</strong> — 46.6% weight</li>
              <li><strong>Consistency</strong> — 29.1% weight</li>
              <li><strong>Racecraft</strong> — 14.9% weight</li>
              <li><strong>Tire Management</strong> — 9.5% weight</li>
            </ul>
            <p className="pillar-note">Validated across 291 driver-races</p>
          </div>

          <div className="pillar">
            <div className="pillar-icon-wrapper">
              <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                <path d="M32 8L40 24L56 26L44 38L47 54L32 46L17 54L20 38L8 26L24 24L32 8Z" fill="#EB0A1E" stroke="#B80818" strokeWidth="2"/>
              </svg>
            </div>
            <h3>Claude AI Coaching</h3>
            <p className="pillar-subtitle">Real AI-Powered Insights</p>
            <ul className="feature-list">
              <li><strong>Corner-by-corner</strong> telemetry analysis</li>
              <li><strong>Personalized</strong> improvement plans</li>
              <li><strong>Strategic</strong> race consultation</li>
              <li><strong>Natural language</strong> Q&A</li>
            </ul>
            <p className="pillar-note">Powered by Anthropic's Claude</p>
          </div>

          <div className="pillar">
            <ChartIcon size="lg" />
            <h3>Making the Predictable Unpredictable</h3>
            <p className="pillar-subtitle">Change Your Outcome</p>
            <ul className="feature-list">
              <li><strong>Practice plans</strong> that target weaknesses</li>
              <li><strong>Track-specific</strong> insights</li>
              <li><strong>Peer comparison</strong> analytics</li>
              <li><strong>Position progression</strong> simulations</li>
            </ul>
            <p className="pillar-note">Your finish is 89% predictable — let's change that</p>
          </div>
        </div>
      )
    },
    {
      id: 'four-factors',
      title: 'Understanding the 4-Factor Performance Model',
      content: (
        <div className="four-factors-section">
          <div className="factor-overview">
            <p>
              The 4-Factor Performance Model breaks down driver performance into four essential dimensions that together reveal your complete racing profile. While raw speed shows how fast you can go, the other three factors—consistency, racecraft, and tire management—determine whether you can sustain that pace under race conditions and execute when it matters.
            </p>
          </div>

          <div className="factor-definitions-grid">
            <div className="factor-card">
              <h4>Speed</h4>
              <p>Measures your raw pace through lap times and sector performance, showing your pure driving ability when pushing to the limit.</p>
            </div>
            <div className="factor-card">
              <h4>Consistency</h4>
              <p>Quantifies how reliably you can reproduce your best performance lap after lap, with lower variation indicating better control and repeatability.</p>
            </div>
            <div className="factor-card">
              <h4>Racecraft</h4>
              <p>Evaluates your wheel-to-wheel racing skills including overtaking efficiency, defensive positioning, and ability to execute race strategy under pressure.</p>
            </div>
            <div className="factor-card">
              <h4>Tire Management</h4>
              <p>Assesses how effectively you preserve tire performance throughout a stint, balancing pace degradation against competitors to maintain speed over longer runs.</p>
            </div>
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
