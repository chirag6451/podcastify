# Google Auth Demo

This application demonstrates Google OAuth authentication with a React frontend and FastAPI backend.

## Project Structure
```
google_auth/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── database.py
└── src/
    ├── components/
    │   └── GoogleAuth.js
    ├── App.js
    └── App.css
```

## Setup and Running

### Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will run on http://localhost:8000

### Frontend
1. In a new terminal, navigate to the project root directory

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```
   The frontend will run on http://localhost:3000

## Features
- Google OAuth authentication
- User data storage in SQLite database
- Frontend-backend integration
- Secure token handling

## Google Authentication Integration Guide

This guide explains how to integrate Google Authentication into your React application with a FastAPI backend. The system handles OAuth 2.0 authentication and stores user data in a SQLite database.

## Prerequisites

- Node.js and npm installed
- Python 3.7+ installed
- A Google Cloud Console account
- Basic knowledge of React and Python

## Setup Guide

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Google OAuth2 API
4. Configure the OAuth consent screen
5. Create OAuth 2.0 Client credentials
6. Add authorized JavaScript origins:
   ```
   http://localhost:3000
   http://localhost:8011
   ```

### 2. Frontend Setup (React)

1. Install required dependencies:
   ```bash
   npm install @react-oauth/google jwt-decode
   ```

2. Create a GoogleAuth component (`GoogleAuth.js`):
   ```javascript
   import React, { useState } from 'react';
   import { GoogleLogin } from '@react-oauth/google';
   import { jwtDecode } from 'jwt-decode';

   const GoogleAuth = () => {
     const [user, setUser] = useState(null);
     const [error, setError] = useState(null);
     const [loading, setLoading] = useState(false);

     const handleSuccess = async (credentialResponse) => {
       try {
         setLoading(true);
         const decoded = jwtDecode(credentialResponse.credential);
         setUser(decoded);

         // Send user data to backend
         const response = await fetch('http://localhost:8011/users/', {
           method: 'POST',
           headers: {
             'Content-Type': 'application/json',
           },
           body: JSON.stringify({
             email: decoded.email,
             name: decoded.name,
             picture: decoded.picture,
             access_token: credentialResponse.credential
           }),
         });

         if (!response.ok) {
           throw new Error('Failed to save user data');
         }
       } catch (err) {
         setError(err.message);
         console.error('Error:', err);
       } finally {
         setLoading(false);
       }
     };

     // ... rest of the component
   };
   ```

3. Update your App component (`App.js`):
   ```javascript
   import { GoogleOAuthProvider } from '@react-oauth/google';
   import GoogleAuth from './components/GoogleAuth';

   function App() {
     return (
       <GoogleOAuthProvider clientId="YOUR_CLIENT_ID">
         <div className="App">
           <GoogleAuth />
         </div>
       </GoogleOAuthProvider>
     );
   }
   ```

### 3. Backend Setup (FastAPI)

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install fastapi uvicorn sqlalchemy google-auth google-auth-oauthlib
   ```

2. Create database models (`models.py`):
   ```python
   from sqlalchemy import Column, Integer, String, DateTime
   from sqlalchemy.ext.declarative import declarative_base
   from datetime import datetime

   Base = declarative_base()

   class User(Base):
       __tablename__ = "users"
       id = Column(Integer, primary_key=True, index=True)
       email = Column(String, unique=True, index=True)
       name = Column(String)
       picture = Column(String)
       access_token = Column(String)
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   ```

3. Set up database connection (`database.py`):
   ```python
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker

   SQLALCHEMY_DATABASE_URL = "sqlite:///./google_auth.db"
   engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

4. Create FastAPI application (`main.py`):
   ```python
   from fastapi import FastAPI, Depends, HTTPException
   from fastapi.middleware.cors import CORSMiddleware
   from sqlalchemy.orm import Session
   from models import Base, User
   from database import engine, get_db

   app = FastAPI()

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

   # Create database tables
   Base.metadata.create_all(bind=engine)
   ```

### 4. Running the Application

1. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8011
   ```

2. Start the React development server:
   ```bash
   npm start
   ```

## Security Considerations

1. Store sensitive information (Client ID, Client Secret) in environment variables
2. Implement proper error handling and validation
3. Use HTTPS in production
4. Implement token refresh mechanism
5. Add rate limiting to prevent abuse
6. Sanitize user input
7. Implement proper session management

## Customization Options

1. **Styling**: Customize the `App.css` file to match your application's theme
2. **Additional User Data**: Modify the User model to store additional information
3. **Scopes**: Add additional Google API scopes based on your needs
4. **Error Handling**: Customize error messages and handling
5. **Loading States**: Add custom loading animations

## Common Issues and Solutions

1. **Redirect URI Mismatch**: Ensure your authorized JavaScript origins in Google Cloud Console match your application URLs
2. **CORS Issues**: Check CORS settings in FastAPI if you're getting cross-origin errors
3. **Database Errors**: Ensure proper database initialization and migrations
4. **Token Validation**: Implement proper token validation and refresh mechanisms

## Production Deployment

### 1. Google Cloud Console Configuration

1. Add your production domains to Google Cloud Console:
   ```
   https://your-frontend-domain.com
   https://api.your-domain.com
   ```
   
2. Add authorized redirect URIs:
   ```
   https://your-frontend-domain.com
   https://your-frontend-domain.com/
   https://your-frontend-domain.com/auth/callback
   ```

3. Update OAuth consent screen:
   - Add your privacy policy URL
   - Add your terms of service URL
   - Add authorized domains
   - If needed, submit for verification (required for sensitive scopes)

### 2. Frontend Changes

1. Update environment variables:
   ```bash
   # .env.production
   REACT_APP_GOOGLE_CLIENT_ID=your_production_client_id
   REACT_APP_API_URL=https://api.your-domain.com
   ```

2. Update API calls in GoogleAuth component:
   ```javascript
   const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8011';
   
   // Update fetch call
   const response = await fetch(`${API_URL}/users/`, {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
     },
     // ... rest of the code
   });
   ```

### 3. Backend Changes

1. Update CORS settings in `main.py`:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "https://your-frontend-domain.com",
           # Include any other domains that need access
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. Set up environment variables:
   ```bash
   # .env
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ALLOWED_ORIGINS=https://your-frontend-domain.com
   GOOGLE_CLIENT_ID=your_production_client_id
   GOOGLE_CLIENT_SECRET=your_production_client_secret
   ```

3. Update database configuration for production:
   ```python
   # database.py
   from os import getenv
   from dotenv import load_dotenv

   load_dotenv()

   SQLALCHEMY_DATABASE_URL = getenv("DATABASE_URL", "sqlite:///./google_auth.db")
   engine = create_engine(
       SQLALCHEMY_DATABASE_URL,
       # Remove sqlite-specific argument for other databases
       connect_args={} if SQLALCHEMY_DATABASE_URL.startswith("postgresql") else {"check_same_thread": False}
   )
   ```

### 4. SSL/TLS Configuration

1. Obtain SSL certificates:
   - Use Let's Encrypt for free certificates
   - Or purchase from a trusted provider

2. Configure Nginx as reverse proxy:
   ```nginx
   # Frontend configuration
   server {
       listen 443 ssl;
       server_name your-frontend-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           root /path/to/react/build;
           try_files $uri $uri/ /index.html;
       }
   }

   # Backend configuration
   server {
       listen 443 ssl;
       server_name api.your-domain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8011;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### 5. Security Checklist for Production

1. **SSL/TLS**:
   - Enable HTTPS only
   - Configure proper SSL settings
   - Set up HSTS
   - Redirect HTTP to HTTPS

2. **Authentication**:
   - Implement rate limiting
   - Add request timeouts
   - Set secure cookie attributes
   - Implement token refresh mechanism

3. **Database**:
   - Use connection pooling
   - Set up regular backups
   - Implement proper indexing
   - Use prepared statements

4. **Monitoring**:
   - Set up error tracking (e.g., Sentry)
   - Implement logging
   - Set up uptime monitoring
   - Configure performance monitoring

5. **Compliance**:
   - Ensure GDPR compliance if applicable
   - Implement proper data retention policies
   - Set up privacy policy
   - Document data handling procedures

### 6. Testing Production Setup

1. Verify Google OAuth flow:
   ```bash
   # Test authentication
   curl -v https://api.your-domain.com/auth/test
   
   # Test CORS
   curl -H "Origin: https://your-frontend-domain.com" \
        -H "Access-Control-Request-Method: POST" \
        -X OPTIONS \
        https://api.your-domain.com/users/
   ```

2. Check SSL configuration:
   ```bash
   # Test SSL setup
   curl -vI https://your-frontend-domain.com
   curl -vI https://api.your-domain.com
   
   # Verify SSL certificate
   openssl s_client -connect your-frontend-domain.com:443
   ```

### 7. Deployment Checklist

- [ ] Update Google Cloud Console settings
- [ ] Configure SSL certificates
- [ ] Update environment variables
- [ ] Set up database backups
- [ ] Configure monitoring tools
- [ ] Test authentication flow
- [ ] Verify CORS settings
- [ ] Check security headers
- [ ] Test error handling
- [ ] Monitor initial user activity

it issues and enhancement requests!

## License





(C) IndaPoint Technologies Private Limited
All rights reserved.

