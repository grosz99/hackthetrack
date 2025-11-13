import { useDriver } from '../../context/DriverContext';
import { useNavigate } from 'react-router-dom';
import RankingsTable from '../../components/RankingsTable/RankingsTable';
import './Rankings.css';

export default function Rankings() {
  const { drivers, loading } = useDriver();
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="rankings-loading">
        <div className="loading-spinner"></div>
        <p>Loading driver rankings...</p>
      </div>
    );
  }

  return (
    <div className="rankings-page">
      <RankingsTable drivers={drivers} />
    </div>
  );
}
