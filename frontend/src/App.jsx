import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { DriverProvider } from './context/DriverContext'
import { ScoutProvider } from './context/ScoutContext'

// Import pages
import ScoutLanding from './pages/ScoutLanding/ScoutLanding'
import Rankings from './pages/Rankings/Rankings'
import TestRankings from './pages/TestRankings'
import Overview from './pages/Overview/Overview'
import RaceLog from './pages/RaceLog/RaceLog'
import Skills from './pages/Skills/Skills'
import Improve from './pages/Improve/Improve'

function App() {
  return (
    <Router>
      <DriverProvider>
        <ScoutProvider>
          <div className="app min-h-screen bg-[#0a0a0a]">
            <main>
              <Routes>
                {/* Rankings - Main landing page */}
                <Route path="/" element={<Rankings />} />
                <Route path="/rankings" element={<Rankings />} />

                {/* Driver detail routes */}
                <Route path="/driver/:driverNumber/overview" element={<Overview />} />
                <Route path="/driver/:driverNumber/race-log" element={<RaceLog />} />
                <Route path="/driver/:driverNumber/skills" element={<Skills />} />
                <Route path="/driver/:driverNumber/improve" element={<Improve />} />

                {/* Legacy routes - redirect to driver detail */}
                <Route path="/overview" element={<Navigate to="/driver/7/overview" replace />} />
                <Route path="/race-log" element={<Navigate to="/driver/7/race-log" replace />} />
                <Route path="/skills" element={<Navigate to="/driver/7/skills" replace />} />
                <Route path="/improve" element={<Navigate to="/driver/7/improve" replace />} />

                {/* Old scout routes - redirect to rankings */}
                <Route path="/scout" element={<Navigate to="/rankings" replace />} />
                <Route path="/scout/driver/:driverNumber/overview" element={<Navigate to="/driver/:driverNumber/overview" replace />} />
                <Route path="/test" element={<TestRankings />} />
              </Routes>
            </main>
          </div>
        </ScoutProvider>
      </DriverProvider>
    </Router>
  )
}

export default App
