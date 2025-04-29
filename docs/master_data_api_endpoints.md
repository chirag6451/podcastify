# Master Data API Endpoints

This document describes the API endpoints for master data in the PodcastAI application, including voices, conversation styles, video styles, profile types, and platforms.

## Base URL

All API endpoints are prefixed with: `http://0.0.0.0:8011/api`

## Authentication

All endpoints require authentication using a JWT token. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Voice Endpoints

### Get All Voices

- **URL**: `/voices/`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Retrieves all available Elevenlabs voices.
- **Response**: Array of voice objects
- **Example Response**:
```json
[
  {
    "voice_id": "adam",
    "name": "Adam",
    "category": "professional",
    "description": "Professional male voice with American accent",
    "gender": "male",
    "accent": "American",
    "age": "adult",
    "language": "english",
    "use_case": "business",
    "preview_url": "",
    "labels": {
      "tone": "professional",
      "clarity": "high"
    },
    "settings": {
      "stability": 0.5,
      "similarity_boost": 0.75
    }
  }
]
```

### Filter Voices

- **URL**: `/voices/filter`
- **Method**: `POST`
- **Auth Required**: Yes
- **Description**: Filters voices based on provided criteria.
- **Request Body**: Filter criteria
- **Example Request**:
```json
{
  "gender": "female",
  "language": "en"
}
```
- **Response**: Array of filtered voice objects
- **Status**: ⚠️ Test failing - returns empty array when filter criteria don't match any voices

### Get Voice by ID

- **URL**: `/voices/{voice_id}`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Retrieves a specific voice by ID.
- **Response**: Voice object

## Conversation Style Endpoints

### Get All Conversation Styles

- **URL**: `/styles/conversation`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Retrieves all available conversation styles.
- **Response**: Array of conversation style objects

### Create Conversation Style

- **URL**: `/styles/conversation`
- **Method**: `POST`
- **Auth Required**: Yes
- **Description**: Creates a new conversation style.
- **Request Body**: Conversation style data
- **Example Request**:
```json
{
  "name": "Casual",
  "description": "Relaxed, informal conversation style suitable for everyday topics"
}
```
- **Response**: Created conversation style object

### Get Conversation Style by ID

- **URL**: `/styles/conversation/{style_id}`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Retrieves a specific conversation style by ID.
- **Response**: Conversation style object

## Video Style Endpoints

### Get All Video Styles

- **URL**: `/styles/video`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Retrieves all available video styles.
- **Response**: Array of video style objects

### Create Video Style

- **URL**: `/styles/video`
- **Method**: `POST`
- **Auth Required**: Yes
- **Description**: Creates a new video style.
- **Request Body**: Video style data
- **Example Request**:
```json
{
  "name": "Minimalist",
  "description": "Clean, simple design with minimal elements"
}
```
- **Response**: Created video style object

### Get Video Style by ID

- **URL**: `/styles/video/{style_id}`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Retrieves a specific video style by ID.
- **Response**: Video style object

## Profile Type Endpoints

### Get All Profile Types

- **URL**: `/styles/profile-types`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Retrieves all available profile types.
- **Response**: Array of profile type objects

### Create Profile Type

- **URL**: `/styles/profile-types`
- **Method**: `POST`
- **Auth Required**: Yes
- **Description**: Creates a new profile type.
- **Request Body**: Profile type data
- **Example Request**:
```json
{
  "name": "Business",
  "description": "Professional profile for business podcasts"
}
```
- **Response**: Created profile type object

### Get Profile Type by ID

- **URL**: `/styles/profile-types/{profile_type_id}`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Retrieves a specific profile type by ID.
- **Response**: Profile type object

## Platform Endpoints

### Get All Platforms

- **URL**: `/styles/platforms`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Retrieves all available platforms.
- **Response**: Array of platform objects

### Create Platform

- **URL**: `/styles/platforms`
- **Method**: `POST`
- **Auth Required**: Yes
- **Description**: Creates a new platform.
- **Request Body**: Platform data
- **Example Request**:
```json
{
  "name": "YouTube",
  "description": "Video sharing platform",
  "icon_url": "https://example.com/youtube-icon.png"
}
```
- **Response**: Created platform object
- **Status**: ⚠️ Test failing - 'description' is an invalid keyword argument for Platform

### Get Platform by ID

- **URL**: `/styles/platforms/{platform_id}`
- **Method**: `GET`
- **Auth Required**: Yes
- **Description**: Retrieves a specific platform by ID.
- **Response**: Platform object

## Known Issues

1. **Voice Filter Endpoint**: The filter endpoint returns an empty array when filter criteria don't match any voices. This is technically correct behavior but causes test failures when checking for voice_id in the response.

2. **Platform Creation**: Creating a platform fails with error "'description' is an invalid keyword argument for Platform". This suggests a mismatch between the API schema and the database model.

## Testing

The master data endpoints can be tested using the provided shell script:

```bash
./api/tests/test_master_data.sh
```

Note that some tests are currently failing due to the issues mentioned above.
