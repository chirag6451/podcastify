# Podcast API Endpoints

## Purpose and Objective
This document provides a comprehensive overview of the podcast-related API endpoints in the PodcastAI application, including podcast management, episode management, and podcast group organization.

## Table of Contents
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Podcast Group Endpoints](#podcast-group-endpoints)
- [Podcast Endpoints](#podcast-endpoints)
- [Episode Endpoints](#episode-endpoints)
- [Platform Config Endpoints](#platform-config-endpoints)
- [Testing](#testing)

## Base URL

All API endpoints are prefixed with: `http://0.0.0.0:8011/api`

## Authentication

All endpoints require authentication using a JWT token. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

To obtain a token, use the [User Login endpoint](/docs/user_api_endpoints.md#user-login).

## Podcast Group Endpoints

Podcast groups allow users to organize their podcasts into logical collections.

### Create Podcast Group

**Endpoint:** `POST /podcasts/groups`

**Request Schema:**
```json
{
  "name": "Business Podcasts",
  "description": "Collection of business-focused podcasts"
}
```

**Response Schema:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Business Podcasts",
  "description": "Collection of business-focused podcasts",
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:00:00Z"
}
```

**Example:**
```bash
curl -X POST "http://0.0.0.0:8011/api/podcasts/groups" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "Business Podcasts", "description": "Collection of business-focused podcasts"}'
```

### Get All Podcast Groups

**Endpoint:** `GET /podcasts/groups`

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100, max: 100)

**Response Schema:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Business Podcasts",
    "description": "Collection of business-focused podcasts",
    "created_at": "2025-04-24T12:00:00Z",
    "updated_at": "2025-04-24T12:00:00Z"
  }
]
```

**Example:**
```bash
curl -X GET "http://0.0.0.0:8011/api/podcasts/groups" \
  -H "Authorization: Bearer <token>"
```

### Get Specific Podcast Group

**Endpoint:** `GET /podcasts/groups/{group_id}`

**Path Parameters:**
- `group_id`: ID of the podcast group to retrieve

**Response Schema:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Business Podcasts",
  "description": "Collection of business-focused podcasts",
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:00:00Z"
}
```

**Example:**
```bash
curl -X GET "http://0.0.0.0:8011/api/podcasts/groups/1" \
  -H "Authorization: Bearer <token>"
```

### Update Podcast Group

**Endpoint:** `PUT /podcasts/groups/{group_id}`

**Path Parameters:**
- `group_id`: ID of the podcast group to update

**Request Schema:**
```json
{
  "name": "Updated Business Podcasts",
  "description": "Updated collection of business-focused podcasts"
}
```

**Response Schema:**
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Updated Business Podcasts",
  "description": "Updated collection of business-focused podcasts",
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:30:00Z"
}
```

**Example:**
```bash
curl -X PUT "http://0.0.0.0:8011/api/podcasts/groups/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "Updated Business Podcasts", "description": "Updated collection of business-focused podcasts"}'
```

### Delete Podcast Group

**Endpoint:** `DELETE /podcasts/groups/{group_id}`

**Path Parameters:**
- `group_id`: ID of the podcast group to delete

**Response:** No content (204)

**Example:**
```bash
curl -X DELETE "http://0.0.0.0:8011/api/podcasts/groups/1" \
  -H "Authorization: Bearer <token>"
```

## Podcast Endpoints

Podcasts are the main content containers that hold episodes.

### Create Podcast

**Endpoint:** `POST /podcasts`

**Request Schema:**
```json
{
  "title": "The Business Innovation Podcast",
  "description": "Exploring innovative business strategies and technologies",
  "language": "en",
  "audience_type": "Business professionals",
  "categories": ["Business", "Technology", "Innovation"],
  "keywords": ["innovation", "business", "technology"],
  "website": "https://example.com/podcast",
  "email": "podcast@example.com",
  "contact_number": "+1234567890",
  "group_id": 1,
  "video_style_id": 1,
  "conversation_style_id": 1,
  "profile_type_id": 1,
  "speaker1_id": 1,
  "speaker2_id": 2
}
```

**Response Schema:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "The Business Innovation Podcast",
  "description": "Exploring innovative business strategies and technologies",
  "cover_image": null,
  "language": "en",
  "audience_type": "Business professionals",
  "categories": ["Business", "Technology", "Innovation"],
  "keywords": ["innovation", "business", "technology"],
  "website": "https://example.com/podcast",
  "email": "podcast@example.com",
  "contact_number": "+1234567890",
  "group_id": 1,
  "video_style_id": 1,
  "conversation_style_id": 1,
  "profile_type_id": 1,
  "speaker1_id": 1,
  "speaker2_id": 2,
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:00:00Z",
  "group": {
    "id": 1,
    "user_id": 1,
    "name": "Business Podcasts",
    "description": "Collection of business-focused podcasts",
    "created_at": "2025-04-24T12:00:00Z",
    "updated_at": "2025-04-24T12:00:00Z"
  }
}
```

**Example:**
```bash
curl -X POST "http://0.0.0.0:8011/api/podcasts" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title": "The Business Innovation Podcast", "description": "Exploring innovative business strategies and technologies", "language": "en", "group_id": 1}'
```

### Get All Podcasts

**Endpoint:** `GET /podcasts`

**Query Parameters:**
- `group_id` (optional): Filter podcasts by group ID
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100, max: 100)

**Response Schema:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "The Business Innovation Podcast",
    "description": "Exploring innovative business strategies and technologies",
    "cover_image": null,
    "language": "en",
    "audience_type": "Business professionals",
    "categories": ["Business", "Technology", "Innovation"],
    "keywords": ["innovation", "business", "technology"],
    "website": "https://example.com/podcast",
    "email": "podcast@example.com",
    "contact_number": "+1234567890",
    "group_id": 1,
    "video_style_id": 1,
    "conversation_style_id": 1,
    "profile_type_id": 1,
    "speaker1_id": 1,
    "speaker2_id": 2,
    "created_at": "2025-04-24T12:00:00Z",
    "updated_at": "2025-04-24T12:00:00Z",
    "group": {
      "id": 1,
      "user_id": 1,
      "name": "Business Podcasts",
      "description": "Collection of business-focused podcasts",
      "created_at": "2025-04-24T12:00:00Z",
      "updated_at": "2025-04-24T12:00:00Z"
    }
  }
]
```

**Example:**
```bash
curl -X GET "http://0.0.0.0:8011/api/podcasts" \
  -H "Authorization: Bearer <token>"
```

### Get Specific Podcast

**Endpoint:** `GET /podcasts/{podcast_id}`

**Path Parameters:**
- `podcast_id`: ID of the podcast to retrieve

**Response Schema:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "The Business Innovation Podcast",
  "description": "Exploring innovative business strategies and technologies",
  "cover_image": null,
  "language": "en",
  "audience_type": "Business professionals",
  "categories": ["Business", "Technology", "Innovation"],
  "keywords": ["innovation", "business", "technology"],
  "website": "https://example.com/podcast",
  "email": "podcast@example.com",
  "contact_number": "+1234567890",
  "group_id": 1,
  "video_style_id": 1,
  "conversation_style_id": 1,
  "profile_type_id": 1,
  "speaker1_id": 1,
  "speaker2_id": 2,
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:00:00Z",
  "group": {
    "id": 1,
    "user_id": 1,
    "name": "Business Podcasts",
    "description": "Collection of business-focused podcasts",
    "created_at": "2025-04-24T12:00:00Z",
    "updated_at": "2025-04-24T12:00:00Z"
  }
}
```

**Example:**
```bash
curl -X GET "http://0.0.0.0:8011/api/podcasts/1" \
  -H "Authorization: Bearer <token>"
```

### Update Podcast

**Endpoint:** `PUT /podcasts/{podcast_id}`

**Path Parameters:**
- `podcast_id`: ID of the podcast to update

**Request Schema:**
```json
{
  "title": "Updated Business Innovation Podcast",
  "description": "Updated description for the podcast",
  "language": "en",
  "audience_type": "Business professionals",
  "categories": ["Business", "Technology", "Innovation"],
  "keywords": ["innovation", "business", "technology"],
  "website": "https://example.com/updated-podcast",
  "email": "updated-podcast@example.com",
  "contact_number": "+9876543210",
  "group_id": 2,
  "video_style_id": 2,
  "conversation_style_id": 2,
  "profile_type_id": 2,
  "speaker1_id": 3,
  "speaker2_id": 4
}
```

**Response Schema:**
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Updated Business Innovation Podcast",
  "description": "Updated description for the podcast",
  "cover_image": null,
  "language": "en",
  "audience_type": "Business professionals",
  "categories": ["Business", "Technology", "Innovation"],
  "keywords": ["innovation", "business", "technology"],
  "website": "https://example.com/updated-podcast",
  "email": "updated-podcast@example.com",
  "contact_number": "+9876543210",
  "group_id": 2,
  "video_style_id": 2,
  "conversation_style_id": 2,
  "profile_type_id": 2,
  "speaker1_id": 3,
  "speaker2_id": 4,
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:30:00Z",
  "group": {
    "id": 2,
    "user_id": 1,
    "name": "Technology Podcasts",
    "description": "Collection of technology-focused podcasts",
    "created_at": "2025-04-24T12:00:00Z",
    "updated_at": "2025-04-24T12:00:00Z"
  }
}
```

**Example:**
```bash
curl -X PUT "http://0.0.0.0:8011/api/podcasts/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"title": "Updated Business Innovation Podcast", "description": "Updated description for the podcast", "group_id": 2}'
```

### Delete Podcast

**Endpoint:** `DELETE /podcasts/{podcast_id}`

**Path Parameters:**
- `podcast_id`: ID of the podcast to delete

**Response:** No content (204)

**Example:**
```bash
curl -X DELETE "http://0.0.0.0:8011/api/podcasts/1" \
  -H "Authorization: Bearer <token>"
```

## Episode Endpoints

Episodes are individual content items within a podcast.

### Create Episode

**Endpoint:** `POST /podcasts/episodes`

**Request Schema:**
```json
{
  "podcast_id": 1,
  "title": "Episode 1: Innovation in the Digital Age",
  "description": "Discussing the latest innovations in digital technology",
  "keywords": ["digital", "innovation", "technology"],
  "language": "en",
  "video_style_id": 1,
  "conversation_style_id": 1,
  "speaker1_id": 1,
  "speaker2_id": 2
}
```

**Response Schema:**
```json
{
  "id": 1,
  "podcast_id": 1,
  "title": "Episode 1: Innovation in the Digital Age",
  "description": "Discussing the latest innovations in digital technology",
  "keywords": ["digital", "innovation", "technology"],
  "language": "en",
  "duration": null,
  "status": "draft",
  "publish_date": null,
  "cover_image": null,
  "video_style_id": 1,
  "conversation_style_id": 1,
  "speaker1_id": 1,
  "speaker2_id": 2,
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:00:00Z"
}
```

**Example:**
```bash
curl -X POST "http://0.0.0.0:8011/api/podcasts/episodes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"podcast_id": 1, "title": "Episode 1: Innovation in the Digital Age", "description": "Discussing the latest innovations in digital technology", "language": "en"}'
```

### Get Specific Episode

**Endpoint:** `GET /podcasts/episodes/{episode_id}`

**Path Parameters:**
- `episode_id`: ID of the episode to retrieve

**Response Schema:**
```json
{
  "id": 1,
  "podcast_id": 1,
  "title": "Episode 1: Innovation in the Digital Age",
  "description": "Discussing the latest innovations in digital technology",
  "keywords": ["digital", "innovation", "technology"],
  "language": "en",
  "duration": null,
  "status": "draft",
  "publish_date": null,
  "cover_image": null,
  "video_style_id": 1,
  "conversation_style_id": 1,
  "speaker1_id": 1,
  "speaker2_id": 2,
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:00:00Z"
}
```

**Example:**
```bash
curl -X GET "http://0.0.0.0:8011/api/podcasts/episodes/1" \
  -H "Authorization: Bearer <token>"
```

### Get All Episodes

**Endpoint:** `GET /podcasts/episodes`

**Query Parameters:**
- `podcast_id` (optional): Filter episodes by podcast ID
- `status` (optional): Filter episodes by status (e.g., 'draft', 'published')
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100, max: 100)

**Response Schema:**
```json
[
  {
    "id": 1,
    "podcast_id": 1,
    "title": "Episode 1: Innovation in the Digital Age",
    "description": "Discussing the latest innovations in digital technology",
    "keywords": ["digital", "innovation", "technology"],
    "language": "en",
    "duration": null,
    "status": "draft",
    "publish_date": null,
    "cover_image": null,
    "video_style_id": 1,
    "conversation_style_id": 1,
    "speaker1_id": 1,
    "speaker2_id": 2,
    "created_at": "2025-04-24T12:00:00Z",
    "updated_at": "2025-04-24T12:00:00Z"
  }
]
```

**Example:**
```bash
curl -X GET "http://0.0.0.0:8011/api/podcasts/episodes?podcast_id=1" \
  -H "Authorization: Bearer <token>"
```

### Get Latest Episodes

**Endpoint:** `GET /podcasts/episodes/latest`

**Query Parameters:**
- `limit` (optional): Maximum number of episodes to return (default: 10, max: 50)

**Response Schema:**
```json
[
  {
    "id": 1,
    "podcast_id": 1,
    "title": "Episode 1: Innovation in the Digital Age",
    "description": "Discussing the latest innovations in digital technology",
    "keywords": ["digital", "innovation", "technology"],
    "language": "en",
    "duration": null,
    "status": "published",
    "publish_date": "2025-04-24T12:00:00Z",
    "cover_image": null,
    "video_style_id": 1,
    "conversation_style_id": 1,
    "speaker1_id": 1,
    "speaker2_id": 2,
    "created_at": "2025-04-24T12:00:00Z",
    "updated_at": "2025-04-24T12:30:00Z"
  }
]
```

**Example:**
```bash
curl -X GET "http://0.0.0.0:8011/api/podcasts/episodes/latest?limit=5" \
  -H "Authorization: Bearer <token>"
```

### Get Scheduled Episodes

**Endpoint:** `GET /podcasts/episodes/scheduled`

**Query Parameters:**
- `days_ahead` (optional): Number of days ahead to look for scheduled episodes (default: 30, max: 365)

**Response Schema:**
```json
[
  {
    "id": 2,
    "podcast_id": 1,
    "title": "Episode 2: Future Trends",
    "description": "Exploring upcoming trends in technology",
    "keywords": ["trends", "future", "technology"],
    "language": "en",
    "duration": null,
    "status": "scheduled",
    "publish_date": "2025-05-01T12:00:00Z",
    "cover_image": null,
    "video_style_id": 1,
    "conversation_style_id": 1,
    "speaker1_id": 1,
    "speaker2_id": 2,
    "created_at": "2025-04-24T12:00:00Z",
    "updated_at": "2025-04-24T12:30:00Z"
  }
]
```

**Example:**
```bash
curl -X GET "http://0.0.0.0:8011/api/podcasts/episodes/scheduled?days_ahead=30" \
  -H "Authorization: Bearer <token>"
```

### Update Episode

**Endpoint:** `PUT /podcasts/episodes/{episode_id}`

**Path Parameters:**
- `episode_id`: ID of the episode to update

**Request Schema:**
```json
{
  "podcast_id": 1,
  "title": "Updated Episode 1: Innovation in the Digital Age",
  "description": "Updated discussion on digital innovations",
  "keywords": ["digital", "innovation", "technology", "update"],
  "language": "en",
  "status": "published",
  "publish_date": "2025-04-25T12:00:00Z",
  "video_style_id": 2,
  "conversation_style_id": 2,
  "speaker1_id": 3,
  "speaker2_id": 4
}
```

**Response Schema:**
```json
{
  "id": 1,
  "podcast_id": 1,
  "title": "Updated Episode 1: Innovation in the Digital Age",
  "description": "Updated discussion on digital innovations",
  "keywords": ["digital", "innovation", "technology", "update"],
  "language": "en",
  "duration": null,
  "status": "published",
  "publish_date": "2025-04-25T12:00:00Z",
  "cover_image": null,
  "video_style_id": 2,
  "conversation_style_id": 2,
  "speaker1_id": 3,
  "speaker2_id": 4,
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:30:00Z"
}
```

**Example:**
```bash
curl -X PUT "http://0.0.0.0:8011/api/podcasts/episodes/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"podcast_id": 1, "title": "Updated Episode 1: Innovation in the Digital Age", "description": "Updated discussion on digital innovations", "status": "published"}'
```

### Update Episode Status

**Endpoint:** `PATCH /podcasts/episodes/{episode_id}/status`

**Path Parameters:**
- `episode_id`: ID of the episode to update

**Request Schema:**
```json
{
  "status": "published"
}
```

**Response Schema:**
```json
{
  "id": 1,
  "podcast_id": 1,
  "title": "Episode 1: Innovation in the Digital Age",
  "description": "Discussing the latest innovations in digital technology",
  "keywords": ["digital", "innovation", "technology"],
  "language": "en",
  "duration": null,
  "status": "published",
  "publish_date": "2025-04-24T12:30:00Z",
  "cover_image": null,
  "video_style_id": 1,
  "conversation_style_id": 1,
  "speaker1_id": 1,
  "speaker2_id": 2,
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:30:00Z"
}
```

**Example:**
```bash
curl -X PATCH "http://0.0.0.0:8011/api/podcasts/episodes/1/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"status": "published"}'
```

### Publish Episode Immediately

**Endpoint:** `POST /podcasts/episodes/{episode_id}/publish`

**Path Parameters:**
- `episode_id`: ID of the episode to publish

**Response Schema:**
```json
{
  "id": 1,
  "podcast_id": 1,
  "title": "Episode 1: Innovation in the Digital Age",
  "description": "Discussing the latest innovations in digital technology",
  "keywords": ["digital", "innovation", "technology"],
  "language": "en",
  "duration": null,
  "status": "published",
  "publish_date": "2025-04-24T12:30:00Z",
  "cover_image": null,
  "video_style_id": 1,
  "conversation_style_id": 1,
  "speaker1_id": 1,
  "speaker2_id": 2,
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:30:00Z"
}
```

**Example:**
```bash
curl -X POST "http://0.0.0.0:8011/api/podcasts/episodes/1/publish" \
  -H "Authorization: Bearer <token>"
```

### Schedule Episode for Future Publishing

**Endpoint:** `POST /podcasts/episodes/{episode_id}/schedule`

**Path Parameters:**
- `episode_id`: ID of the episode to schedule

**Request Schema:**
```json
{
  "publish_date": "2025-05-01T12:00:00Z"
}
```

**Response Schema:**
```json
{
  "id": 1,
  "podcast_id": 1,
  "title": "Episode 1: Innovation in the Digital Age",
  "description": "Discussing the latest innovations in digital technology",
  "keywords": ["digital", "innovation", "technology"],
  "language": "en",
  "duration": null,
  "status": "scheduled",
  "publish_date": "2025-05-01T12:00:00Z",
  "cover_image": null,
  "video_style_id": 1,
  "conversation_style_id": 1,
  "speaker1_id": 1,
  "speaker2_id": 2,
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:30:00Z"
}
```

**Example:**
```bash
curl -X POST "http://0.0.0.0:8011/api/podcasts/episodes/1/schedule" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"publish_date": "2025-05-01T12:00:00Z"}'
```

### Delete Episode

**Endpoint:** `DELETE /podcasts/episodes/{episode_id}`

**Path Parameters:**
- `episode_id`: ID of the episode to delete

**Response:** No content (204)

**Example:**
```bash
curl -X DELETE "http://0.0.0.0:8011/api/podcasts/episodes/1" \
  -H "Authorization: Bearer <token>"
```

## Platform Config Endpoints

Platform configs define how podcasts are published to external platforms.

### Create Platform Config

**Endpoint:** `POST /podcasts/platform-configs`

**Request Schema:**
```json
{
  "podcast_id": 1,
  "platform_id": 1,
  "enabled": true,
  "auto_publish": false,
  "account_id": "platform_account_123",
  "api_key": "api_key_456",
  "settings": {
    "category": "Technology",
    "explicit": false
  }
}
```

**Response Schema:**
```json
{
  "id": 1,
  "podcast_id": 1,
  "platform_id": 1,
  "enabled": true,
  "auto_publish": false,
  "account_id": "platform_account_123",
  "api_key": "api_key_456",
  "settings": {
    "category": "Technology",
    "explicit": false
  },
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:00:00Z"
}
```

**Example:**
```bash
curl -X POST "http://0.0.0.0:8011/api/podcasts/platform-configs" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"podcast_id": 1, "platform_id": 1, "enabled": true, "account_id": "platform_account_123"}'
```

### Get Specific Platform Config

**Endpoint:** `GET /podcasts/platform-configs/{config_id}`

**Path Parameters:**
- `config_id`: ID of the platform config to retrieve

**Response Schema:**
```json
{
  "id": 1,
  "podcast_id": 1,
  "platform_id": 1,
  "enabled": true,
  "auto_publish": false,
  "account_id": "platform_account_123",
  "api_key": "api_key_456",
  "settings": {
    "category": "Technology",
    "explicit": false
  },
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:00:00Z"
}
```

**Example:**
```bash
curl -X GET "http://0.0.0.0:8011/api/podcasts/platform-configs/1" \
  -H "Authorization: Bearer <token>"
```

### Get All Platform Configs

**Endpoint:** `GET /podcasts/platform-configs`

**Query Parameters:**
- `podcast_id` (optional): Filter configs by podcast ID
- `platform_id` (optional): Filter configs by platform ID
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Maximum number of records to return (default: 100, max: 100)

**Response Schema:**
```json
[
  {
    "id": 1,
    "podcast_id": 1,
    "platform_id": 1,
    "enabled": true,
    "auto_publish": false,
    "account_id": "platform_account_123",
    "api_key": "api_key_456",
    "settings": {
      "category": "Technology",
      "explicit": false
    },
    "created_at": "2025-04-24T12:00:00Z",
    "updated_at": "2025-04-24T12:00:00Z"
  }
]
```

**Example:**
```bash
curl -X GET "http://0.0.0.0:8011/api/podcasts/platform-configs?podcast_id=1" \
  -H "Authorization: Bearer <token>"
```

### Update Platform Config

**Endpoint:** `PUT /podcasts/platform-configs/{config_id}`

**Path Parameters:**
- `config_id`: ID of the platform config to update

**Request Schema:**
```json
{
  "podcast_id": 1,
  "platform_id": 1,
  "enabled": true,
  "auto_publish": true,
  "account_id": "updated_account_123",
  "api_key": "updated_key_456",
  "settings": {
    "category": "Business",
    "explicit": true
  }
}
```

**Response Schema:**
```json
{
  "id": 1,
  "podcast_id": 1,
  "platform_id": 1,
  "enabled": true,
  "auto_publish": true,
  "account_id": "updated_account_123",
  "api_key": "updated_key_456",
  "settings": {
    "category": "Business",
    "explicit": true
  },
  "created_at": "2025-04-24T12:00:00Z",
  "updated_at": "2025-04-24T12:30:00Z"
}
```

**Example:**
```bash
curl -X PUT "http://0.0.0.0:8011/api/podcasts/platform-configs/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"podcast_id": 1, "platform_id": 1, "enabled": true, "auto_publish": true, "account_id": "updated_account_123"}'
```

### Delete Platform Config

**Endpoint:** `DELETE /podcasts/platform-configs/{config_id}`

**Path Parameters:**
- `config_id`: ID of the platform config to delete

**Response:** No content (204)

**Example:**
```bash
curl -X DELETE "http://0.0.0.0:8011/api/podcasts/platform-configs/1" \
  -H "Authorization: Bearer <token>"
```

## Testing

To test the podcast API endpoints, you can use the provided test script:

```bash
./api/tests/test_podcast_fixed.sh
```

This script tests all the podcast-related endpoints, including podcast groups, podcasts, episodes, and platform configs.

For more information on testing, see the [Testing Documentation](/docs/testing.md).
