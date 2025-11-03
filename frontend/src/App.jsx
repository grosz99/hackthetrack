import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'

// Import pages
import Overview from './pages/Overview/Overview'
import RaceLog from './pages/RaceLog/RaceLog'
import Skills from './pages/Skills/Skills'
import Improve from './pages/Improve/Improve'

function App() {
  return (
    <Router>
      <div className="app min-h-screen bg-bg-primary">
        <main>
          <Routes>
            <Route path="/" element={<Navigate to="/overview" replace />} />
            <Route path="/overview" element={<Overview />} />
            <Route path="/race-log" element={<RaceLog />} />
            <Route path="/skills" element={<Skills />} />
            <Route path="/improve" element={<Improve />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
