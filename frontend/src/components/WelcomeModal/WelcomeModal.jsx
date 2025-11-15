import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';
import { TrophyIcon, TargetIcon, ChartIcon } from '../icons';
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
          <TrophyIcon size="xxl" />
          <p className="intro-text">
            Welcome to HackTheTrack — where validated statistics meet AI-powered coaching to transform your racing performance.
          </p>
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
                <path d="M32 8L40 24L56 26L44 38L47 54L32 46L17 54L20 38L8 26L24 24L32 8Z" fill="#e74c3c" stroke="#c0392b" strokeWidth="2"/>
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
      id: 'honesty',
      title: 'What We Are (And Aren\'t)',
      content: (
        <div className="honesty-section">
          <div className="honesty-column yes">
            <h3>What We Offer</h3>
            <ul>
              <li><strong>Validated statistical framework</strong> — 89.5% accuracy in explaining finish positions from historical data</li>
              <li><strong>Real Claude AI coaching</strong> — Anthropic's LLM analyzing your telemetry with race engineering expertise</li>
              <li><strong>Evidence-based scoring</strong> — Every metric backed by regression analysis on 291 driver-races</li>
              <li><strong>Honest uncertainty</strong> — We show you the data, not guarantees</li>
            </ul>
          </div>

          <div className="honesty-column no">
            <h3>What We Don't Claim</h3>
            <ul>
              <li><strong>Not a crystal ball</strong> — We score current performance, we don't predict future race outcomes</li>
              <li><strong>Not "AI predictions"</strong> — Our model uses statistical regression coefficients, not neural networks</li>
              <li><strong>Not magic</strong> — Improvement requires practice and seat time, not just data</li>
              <li><strong>Not comprehensive</strong> — Currently focused on GR Cup data (more series coming)</li>
            </ul>
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
