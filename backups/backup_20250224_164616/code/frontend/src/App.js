import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { GoogleOAuthProvider } from '@react-oauth/google';
import GoogleAuth from './components/GoogleAuth';
import './App.css';

function App() {
  return (
    <GoogleOAuthProvider clientId="577155825398-pg20jk65d3ksgf16vbtirnmvraq8kvff.apps.googleusercontent.com">
      <Router>
        <div className="App">
          <header className="App-header">
            <h1>Google Authentication Demo</h1>
            <GoogleAuth />
          </header>
        </div>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
