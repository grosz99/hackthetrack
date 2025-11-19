import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { DriverProvider } from './context/DriverContext'
import { ScoutProvider } from './context/ScoutContext'

// Import pages
import Rankings from './pages/Rankings/Rankings'
import Overview from './pages/Overview/Overview'
import RaceLog from './pages/RaceLog/RaceLog'
import Skills from './pages/Skills/Skills'
import Improve from './pages/Improve/Improve'
import TrackIntelligence from './pages/TrackIntelligence/TrackIntelligence'
import StrategyChat from './pages/StrategyChat/StrategyChat'
import TelemetryComparison from './pages/TelemetryComparison/TelemetryComparison'

function App() {
  return (
    <Router>
      <DriverProvider>
        <ScoutProvider>
          <div className="app min-h-screen bg-bg-primary">
            <main>
              <Routes>
                {/* Rankings - Main landing page */}
                <Route path="/" element={<Rankings />} />
                <Route path="/rankings" element={<Rankings />} />

                {/* Driver detail routes */}
                <Route path="/driver/:driverNumber/overview" element={<Overview />} />
                <Route path="/driver/:driverNumber/race-log" element={<RaceLog />} />
                <Route path="/driver/:driverNumber/skills" element={<Skills />} />
                <Route path="/driver/:driverNumber/driver-development" element={<Improve />} />
                <Route path="/driver/:driverNumber/telemetry-comparison" element={<TelemetryComparison />} />
                <Route path="/driver/:driverNumber/strategy-chat" element={<StrategyChat />} />

                {/* Legacy improve route redirect */}
                <Route path="/driver/:driverNumber/improve" element={<Navigate to="/driver/:driverNumber/driver-development" replace />} />

                {/* Track Intelligence - Global feature not driver-specific */}
                <Route path="/track-intelligence" element={<TrackIntelligence />} />

                {/* Legacy routes - redirect to driver detail */}
                <Route path="/overview" element={<Navigate to="/driver/7/overview" replace />} />
                <Route path="/race-log" element={<Navigate to="/driver/7/race-log" replace />} />
                <Route path="/skills" element={<Navigate to="/driver/7/skills" replace />} />
                <Route path="/improve" element={<Navigate to="/driver/7/driver-development" replace />} />
                <Route path="/driver-development" element={<Navigate to="/driver/7/driver-development" replace />} />

                {/* Old scout routes - redirect to rankings */}
                <Route path="/scout" element={<Navigate to="/rankings" replace />} />
                <Route path="/scout/driver/:driverNumber/overview" element={<Navigate to="/driver/:driverNumber/overview" replace />} />
              </Routes>
            </main>
          </div>
        </ScoutProvider>
      </DriverProvider>
    </Router>
  )
}

export default App
