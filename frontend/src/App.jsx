import React from 'react'
import { GoogleOAuthProvider } from '@react-oauth/google';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import GoogleAuth from './components/GoogleAuth'
import Dashboard from './components/Dashboard'
import './App.css'

function App() {
  return (
    <GoogleOAuthProvider clientId="577155825398-pg20jk65d3ksgf16vbtirnmvraq8kvff.apps.googleusercontent.com">
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<GoogleAuth />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </Router>
    </GoogleOAuthProvider>
  )
}

export default App
