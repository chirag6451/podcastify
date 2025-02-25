import React from 'react'
import { GoogleOAuthProvider } from '@react-oauth/google';
import GoogleAuth from './components/GoogleAuth'
import './App.css'

function App() {
  return (
    <GoogleOAuthProvider clientId="577155825398-pg20jk65d3ksgf16vbtirnmvraq8kvff.apps.googleusercontent.com">
      <div className="App">
        <h1>Google Authentication Demo</h1>
        <GoogleAuth />
      </div>
    </GoogleOAuthProvider>
  )
}

export default App
