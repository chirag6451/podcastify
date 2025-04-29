# User API Endpoints Documentation

## Purpose and Objective
This document provides comprehensive documentation for all user-related API endpoints in the PodcastAI platform. It includes authentication flows, request/response schemas, and usage examples for both backend and frontend developers.

## Table of Contents
- [Authentication](#authentication)
- [User Registration](#user-registration)
- [User Login](#user-login)
- [User Profile](#user-profile)
- [User Settings](#user-settings)
- [Business Information](#business-information)
- [Password Management](#password-management)
- [Testing](#testing)

## Authentication

The API uses JWT (JSON Web Token) based authentication. Protected endpoints require a valid Bearer token in the Authorization header.

### Token Format

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzQ4MTU4NTA4fQ.CnZbki-f4tUwEKcFT_c6SY89FyX-5acmxeLSHG6f4FY
```

### Token Lifespan

Tokens are valid for 30 days from issuance. After expiration, users must log in again to obtain a new token.

## User Registration

Register a new user account.

- **URL**: `/users/register`
- **Method**: `POST`
- **Authentication**: None

### Request Schema

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

### Response Schema

```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "id": 1,
  "profile_picture": null,
  "created_at": "2025-04-25T07:28:46.213631",
  "updated_at": "2025-04-25T07:28:46.213631"
}
```

### Error Responses

- **409 Conflict**: Email already exists
  ```json
  {
    "detail": "Email already registered"
  }
  ```

- **422 Validation Error**: Invalid input
  ```json
  {
    "detail": [
      {
        "loc": ["body", "email"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

## User Login

Authenticate a user and receive an access token.

- **URL**: `/users/login`
- **Method**: `POST`
- **Authentication**: None

### Request Schema

```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

### Response Schema

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzQ4MTU4NTA4fQ.CnZbki-f4tUwEKcFT_c6SY89FyX-5acmxeLSHG6f4FY",
  "token_type": "bearer"
}
```

### Error Responses

- **401 Unauthorized**: Invalid credentials
  ```json
  {
    "detail": "Incorrect email or password"
  }
  ```

## User Profile

### Get Current User Profile

Retrieve the profile of the currently authenticated user.

- **URL**: `/users/me`
- **Method**: `GET`
- **Authentication**: Required

### Response Schema

```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "id": 1,
  "profile_picture": "https://example.com/profile.jpg",
  "created_at": "2025-04-25T07:28:46.213631",
  "updated_at": "2025-04-25T07:28:46.213631"
}
```

### Update User Profile

Update the profile of the currently authenticated user.

- **URL**: `/users/me`
- **Method**: `PUT`
- **Authentication**: Required

### Request Schema

```json
{
  "name": "Updated Name",
  "profile_picture": "https://example.com/new-profile.jpg"
}
```

### Response Schema

```json
{
  "email": "user@example.com",
  "name": "Updated Name",
  "id": 1,
  "profile_picture": "https://example.com/new-profile.jpg",
  "created_at": "2025-04-25T07:28:46.213631",
  "updated_at": "2025-04-25T07:35:21.978913"
}
```

## User Settings

### Get User Settings

Retrieve the settings of the currently authenticated user.

- **URL**: `/users/settings`
- **Method**: `GET`
- **Authentication**: Required

### Response Schema

```json
{
  "autopilot_mode": true,
  "default_voice1_id": "eleven_monolingual_v1",
  "default_voice2_id": "eleven_multilingual_v2",
  "default_language": "en",
  "default_video_style_id": 1,
  "default_conversation_style_id": 2,
  "default_duration": "30:00",
  "user_id": 1,
  "created_at": "2025-04-25T07:28:46.213631",
  "updated_at": "2025-04-25T07:28:46.213631"
}
```

### Update User Settings

Update the settings of the currently authenticated user.

- **URL**: `/users/settings`
- **Method**: `PUT`
- **Authentication**: Required

### Request Schema

```json
{
  "autopilot_mode": true,
  "default_voice1_id": "eleven_monolingual_v1",
  "default_voice2_id": "eleven_multilingual_v2",
  "default_language": "en",
  "default_video_style_id": 1,
  "default_conversation_style_id": 2,
  "default_duration": "30:00"
}
```

All fields are optional. Only include the fields you want to update.

### Response Schema

```json
{
  "autopilot_mode": true,
  "default_voice1_id": "eleven_monolingual_v1",
  "default_voice2_id": "eleven_multilingual_v2",
  "default_language": "en",
  "default_video_style_id": 1,
  "default_conversation_style_id": 2,
  "default_duration": "30:00",
  "user_id": 1,
  "created_at": "2025-04-25T07:28:46.213631",
  "updated_at": "2025-04-25T07:35:21.978913"
}
```

## Business Information

### Create Business Information

Create business information for the currently authenticated user.

- **URL**: `/users/business`
- **Method**: `POST`
- **Authentication**: Required

### Request Schema

```json
{
  "business_name": "My Business",
  "business_email": "business@example.com",
  "business_type": "Technology",
  "business_website": "https://example.com",
  "instagram_handle": "mybusiness",
  "linkedin_url": "https://linkedin.com/in/mybusiness",
  "facebook_url": "https://facebook.com/mybusiness",
  "business_description": "A description of my business",
  "target_audience": "Technology enthusiasts"
}
```

All fields except `business_name` are optional.

### Response Schema

```json
{
  "business_name": "My Business",
  "business_email": "business@example.com",
  "business_type": "Technology",
  "business_website": "https://example.com",
  "instagram_handle": "mybusiness",
  "linkedin_url": "https://linkedin.com/in/mybusiness",
  "facebook_url": "https://facebook.com/mybusiness",
  "business_description": "A description of my business",
  "target_audience": "Technology enthusiasts",
  "id": 1,
  "user_id": 1,
  "created_at": "2025-04-25T07:33:45.853048",
  "updated_at": "2025-04-25T07:33:45.853048"
}
```

### Get Business Information

Retrieve the business information of the currently authenticated user.

- **URL**: `/users/business`
- **Method**: `GET`
- **Authentication**: Required

### Response Schema

```json
{
  "business_name": "My Business",
  "business_email": "business@example.com",
  "business_type": "Technology",
  "business_website": "https://example.com",
  "instagram_handle": "mybusiness",
  "linkedin_url": "https://linkedin.com/in/mybusiness",
  "facebook_url": "https://facebook.com/mybusiness",
  "business_description": "A description of my business",
  "target_audience": "Technology enthusiasts",
  "id": 1,
  "user_id": 1,
  "created_at": "2025-04-25T07:33:45.853048",
  "updated_at": "2025-04-25T07:33:45.853048"
}
```

### Update Business Information

Update the business information of the currently authenticated user.

- **URL**: `/users/business`
- **Method**: `PUT`
- **Authentication**: Required

### Request Schema

```json
{
  "business_name": "Updated Business Name",
  "business_email": "updated@example.com",
  "business_type": "Media",
  "business_website": "https://updated-example.com",
  "instagram_handle": "updatedbusiness",
  "linkedin_url": "https://linkedin.com/in/updatedbusiness",
  "facebook_url": "https://facebook.com/updatedbusiness",
  "business_description": "An updated description of my business",
  "target_audience": "Media enthusiasts"
}
```

All fields are optional. Only include the fields you want to update.

### Response Schema

```json
{
  "business_name": "Updated Business Name",
  "business_email": "updated@example.com",
  "business_type": "Media",
  "business_website": "https://updated-example.com",
  "instagram_handle": "updatedbusiness",
  "linkedin_url": "https://linkedin.com/in/updatedbusiness",
  "facebook_url": "https://facebook.com/updatedbusiness",
  "business_description": "An updated description of my business",
  "target_audience": "Media enthusiasts",
  "id": 1,
  "user_id": 1,
  "created_at": "2025-04-25T07:33:45.853048",
  "updated_at": "2025-04-25T07:35:21.999344"
}
```

## Password Management

### Change Password

Change the password of the currently authenticated user.

- **URL**: `/users/change-password`
- **Method**: `POST`
- **Authentication**: Required

### Request Schema

```json
{
  "current_password": "currentpassword123",
  "new_password": "newpassword456"
}
```

### Response Schema

```json
{
  "message": "Password changed successfully"
}
```

### Error Responses

- **401 Unauthorized**: Incorrect current password
  ```json
  {
    "detail": "Incorrect current password"
  }
  ```

### Request Password Reset

Request a password reset for a user by email.

- **URL**: `/users/reset-password/request`
- **Method**: `POST`
- **Authentication**: None

### Request Schema

```json
{
  "email": "user@example.com"
}
```

### Response Schema

```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

In development mode, the response also includes a debug token:

```json
{
  "message": "If the email exists, a password reset link has been sent",
  "debug_token": "5ddb8234-f1e6-41f6-8b70-4da41cb381ba"
}
```

### Confirm Password Reset

Confirm a password reset using the token received by email.

- **URL**: `/users/reset-password/confirm`
- **Method**: `POST`
- **Authentication**: None

### Request Schema

```json
{
  "token": "5ddb8234-f1e6-41f6-8b70-4da41cb381ba",
  "new_password": "resetpassword789"
}
```

### Response Schema

```json
{
  "message": "Password has been reset successfully"
}
```

### Error Responses

- **400 Bad Request**: Invalid or expired token
  ```json
  {
    "detail": "Invalid or expired token"
  }
  ```

## Testing

The API includes comprehensive test scripts to verify all user-related endpoints. These tests can be found in the `/api/tests/` directory:

- `test_user_complete.sh`: Tests the complete user journey from registration to password reset
- `test_user_auth.sh`: Tests user registration, login, profile, and password change
- `test_user_settings.sh`: Tests user settings and business information endpoints
- `test_password_reset.sh`: Tests password reset functionality
- `run_user_tests.sh`: Runs all user endpoint test scripts in sequence

### Running Tests

To run all user API tests:

```bash
cd /path/to/podcraftai
./api/tests/run_user_tests.sh
```

To run the complete user journey test:

```bash
cd /path/to/podcraftai
./api/tests/test_user_complete.sh
```

## Implementation Notes

### Frontend Integration

When integrating with a frontend application:

1. Store the JWT token securely (preferably in HttpOnly cookies or secure local storage)
2. Include the token in the Authorization header for all authenticated requests
3. Implement token refresh or redirect to login when the token expires
4. Handle error responses appropriately and display user-friendly messages

### Backend Implementation Details

- All endpoints use FastAPI with Pydantic schemas for request/response validation
- Password hashing uses bcrypt for secure storage
- JWT tokens are signed with a secret key and include the user's email and expiration time
- Database models use SQLAlchemy ORM with PostgreSQL
- Password reset tokens are stored in the database with expiration and usage tracking

## Security Considerations

- All passwords are hashed using bcrypt before storage
- JWT tokens have a limited lifespan (30 days)
- Password reset tokens expire after 24 hours and can only be used once
- All sensitive endpoints require authentication
- Input validation is performed using Pydantic schemas
- Error messages are designed to prevent information leakage
