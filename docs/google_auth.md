# Google Authentication Flow Documentation

## Overview

This document outlines the Google OAuth 2.0 authentication flow implemented in the PodcastAI application. The authentication system allows users to authenticate with their Google accounts and grants the application access to YouTube, Gmail, and Google Drive APIs.

## Authentication Components

### Frontend Components

- **Main Authentication Page**: `http://localhost:3000`
- **Authentication Component**: `GoogleAuth.js` 
- **OAuth Provider**: `@react-oauth/google` library

### Backend Components

- **Callback Endpoint**: `http://localhost:8011/api/auth/google/callback`
- **Token Refresh Endpoint**: `http://localhost:8011/api/auth/google/refresh`
- **Database Table**: `google_auth`

## Authentication Flow

### Step 1: User Initiates Authentication

1. User navigates to `http://localhost:3000`
2. The page displays a "Google Authentication Demo" with a "Sign in with Google" button
3. User clicks the button to initiate the authentication process

### Step 2: Google OAuth Consent

1. User is redirected to Google's OAuth consent screen
2. The consent screen requests permissions for:
   - YouTube (upload, manage videos)
   - Gmail (read, send emails)
   - Google Drive (file access)
   - User profile information

### Step 3: Authorization Code Exchange

1. After user grants permissions, Google redirects back to the application with an authorization code
2. The frontend sends this code to the backend endpoint: `http://localhost:8011/api/auth/google/callback`
3. The backend exchanges this code for access and refresh tokens using Google's token endpoint

### Step 4: Token Storage

1. The backend stores the following information in the `google_auth` table:
   - `user_id`: Google's unique identifier for the user
   - `email`: User's email address
   - `google_id`: Same as user_id
   - `access_token`: Short-lived token for API access
   - `refresh_token`: Long-lived token for refreshing access tokens
   - `token_uri`: Google's token endpoint
   - `client_id`: Application's client ID
   - `client_secret`: Application's client secret
   - `profile_data`: JSON with user profile information
   - `token_expiry`: Expiration timestamp for the access token

### Step 5: User Redirection

1. After successful authentication, the user is redirected to the dashboard page
2. The user's email and ID are stored in localStorage for session management

## Token Refresh Mechanism

The application includes an automatic token refresh mechanism:

1. Before making API calls, the system checks if the access token is expired
2. If expired, it uses the refresh token to obtain a new access token
3. The new access token is stored in the database with an updated expiry time

## API Endpoints

### Authentication Callback

- **URL**: `http://localhost:8011/api/auth/google/callback`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "code": "authorization_code_from_google"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "user_id": "google_user_id",
    "email": "user@example.com",
    "name": "User Name",
    "picture": "profile_picture_url"
  }
  ```

### Token Refresh

- **URL**: `http://localhost:8011/api/auth/google/refresh?user_id=USER_ID`
- **Method**: GET
- **Response**:
  ```json
  {
    "success": true,
    "access_token": "new_access_token"
  }
  ```

## Database Schema

The `google_auth` table has the following structure:

```sql
CREATE TABLE google_auth (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    google_id VARCHAR(255) NOT NULL UNIQUE,
    access_token TEXT,
    refresh_token TEXT,
    token_uri TEXT,
    client_id TEXT,
    client_secret TEXT,
    token_expiry TIMESTAMP,
    profile_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email)
);
```

## OAuth Configuration

- **Client ID**: `577155825398-pg20jk65d3ksgf16vbtirnmvraq8kvff.apps.googleusercontent.com`
- **Redirect URI**: `http://localhost:3000`
- **Scopes**:
  - `https://www.googleapis.com/auth/userinfo.email`
  - `https://www.googleapis.com/auth/userinfo.profile`
  - `https://mail.google.com/`
  - `https://www.googleapis.com/auth/gmail.modify`
  - `https://www.googleapis.com/auth/gmail.compose`
  - `https://www.googleapis.com/auth/gmail.send`
  - `https://www.googleapis.com/auth/drive`
  - `https://www.googleapis.com/auth/drive.file`
  - `https://www.googleapis.com/auth/drive.appdata`
  - `https://www.googleapis.com/auth/drive.metadata`
  - `https://www.googleapis.com/auth/youtube`
  - `https://www.googleapis.com/auth/youtube.upload`
  - `https://www.googleapis.com/auth/youtube.force-ssl`

## Using Google Services After Authentication

After authentication, the application can use the stored tokens to access Google services:

1. Retrieve the user's credentials from the `google_auth` table
2. Create a `Credentials` object using the Google Auth library
3. Use these credentials to initialize service clients (YouTube, Gmail, Drive)
4. Make API calls using these service clients

Example code for initializing a YouTube service:

```python
def get_youtube_service(user_email):
    """Get authenticated YouTube service"""
    db = PodcastDB()
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            # Get OAuth credentials
            cur.execute("""
                SELECT 
                    access_token,
                    refresh_token,
                    token_uri,
                    client_id,
                    client_secret
                FROM google_auth 
                WHERE email = %s
            """, (user_email,))
            result = cur.fetchone()
            if not result:
                raise Exception(f"No Google credentials found for {user_email}")
            
            access_token, refresh_token, token_uri, client_id, client_secret = result
            
            # Create credentials
            creds = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri=token_uri,
                client_id=client_id,
                client_secret=client_secret,
                scopes=["https://www.googleapis.com/auth/youtube.upload",
                       "https://www.googleapis.com/auth/youtube"]
            )
            
            # Build service
            return build("youtube", "v3", credentials=creds)
```

## Troubleshooting

If authentication issues occur:

1. Check if the user has valid tokens in the `google_auth` table
2. Verify that the tokens haven't expired (check `token_expiry`)
3. If tokens are expired, try using the refresh endpoint
4. If refresh fails, the user needs to re-authenticate
