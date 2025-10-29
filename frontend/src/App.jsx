import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import TrackIntelligence from './pages/TrackIntelligence'
import StrategyChat from './pages/StrategyChat'
import TelemetryComparison from './pages/TelemetryComparison'
import Navigation from './components/Navigation'

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <Routes>
          <Route path="/" element={<Navigate to="/track-intelligence" replace />} />
          <Route path="/track-intelligence" element={<TrackIntelligence />} />
          <Route path="/strategy" element={<StrategyChat />} />
          <Route path="/telemetry" element={<TelemetryComparison />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
