import { useState, useEffect } from 'react';
import { useDriver } from '../../context/DriverContext';
import { useNavigate } from 'react-router-dom';
import RankingsTable from '../../components/RankingsTable/RankingsTable';
import WelcomeModal from '../../components/WelcomeModal';
import './Rankings.css';

export default function Rankings() {
  const { drivers, loading } = useDriver();
  const navigate = useNavigate();
  const [showWelcome, setShowWelcome] = useState(false);

  useEffect(() => {
    // Check if user has seen welcome modal
    const hasSeenWelcome = localStorage.getItem('httt_welcome_seen');
    if (!hasSeenWelcome && !loading) {
      // Small delay for dramatic entrance after data loads
      setTimeout(() => setShowWelcome(true), 500);
    }
  }, [loading]);

  const handleCloseWelcome = () => {
    localStorage.setItem('httt_welcome_seen', 'true');
    setShowWelcome(false);
  };

  if (loading) {
    return (
      <div className="rankings-loading">
        <div className="loading-spinner"></div>
        <p>Loading driver rankings...</p>
      </div>
    );
  }

  const handleReopenWelcome = () => {
    setShowWelcome(true);
  };

  return (
    <div className="rankings-page">
      {showWelcome && <WelcomeModal onClose={handleCloseWelcome} />}
      <RankingsTable drivers={drivers} onShowInfo={handleReopenWelcome} />
    </div>
  );
}
