import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { DriverProvider } from './context/DriverContext'
import { ScoutProvider } from './context/ScoutContext'

// Import pages
import ScoutLanding from './pages/ScoutLanding/ScoutLanding'
import Overview from './pages/Overview/Overview'
import RaceLog from './pages/RaceLog/RaceLog'
import Skills from './pages/Skills/Skills'
import Improve from './pages/Improve/Improve'

function App() {
  return (
    <Router>
      <DriverProvider>
        <ScoutProvider>
          <div className="app min-h-screen bg-bg-primary">
            <main>
              <Routes>
                {/* Scout Portal - New entry point */}
                <Route path="/" element={<Navigate to="/scout" replace />} />
                <Route path="/scout" element={<ScoutLanding />} />

                {/* Scout-specific driver routes */}
                <Route path="/scout/driver/:driverNumber/overview" element={<Overview />} />
                <Route path="/scout/driver/:driverNumber/race-log" element={<RaceLog />} />
                <Route path="/scout/driver/:driverNumber/skills" element={<Skills />} />
                <Route path="/scout/driver/:driverNumber/improve" element={<Improve />} />

                {/* Legacy routes (backwards compatibility) */}
                <Route path="/overview" element={<Overview />} />
                <Route path="/race-log" element={<RaceLog />} />
                <Route path="/skills" element={<Skills />} />
                <Route path="/improve" element={<Improve />} />
              </Routes>
            </main>
          </div>
        </ScoutProvider>
      </DriverProvider>
    </Router>
  )
}

export default App
