# PodcastAI Database Structure Documentation

## Purpose and Objective
This document provides a comprehensive overview of the PodcastAI database structure, including tables, relationships, and key fields. It serves as a reference for developers working on the platform to understand the data model and relationships between different entities.

## Core Tables

### 1. Users and Authentication

#### `users`
- **Primary Key**: `id` (integer)
- **Unique Fields**: `email`
- **Key Fields**: `name`, `password_hash`, `profile_picture`, `created_at`, `updated_at`
- **Relationships**:
  - One-to-One with `user_settings`
  - One-to-One with `business_information`
  - One-to-Many with `podcasts`, `podcast_groups`, `speakers`, `credits`, `credit_usage`, `subscriptions`, `transactions`, `payment_methods`, `password_resets`

#### `password_resets`
- **Primary Key**: `id` (integer)
- **Key Fields**: `user_id`, `token`, `is_used`, `expires_at`, `created_at`
- **Foreign Keys**: `user_id` references `users(id)`

### 2. User Settings and Preferences

#### `user_settings`
- **Primary Key**: `user_id` (integer)
- **Key Fields**: `autopilot_mode`, `default_voice1_id`, `default_voice2_id`, `default_language`, `default_video_style_id`, `default_conversation_style_id`, `default_duration`, `created_at`, `updated_at`
- **Foreign Keys**:
  - `user_id` references `users(id)`
  - `default_voice1_id` references `elevenlabs_voices(voice_id)`
  - `default_voice2_id` references `elevenlabs_voices(voice_id)`
  - `default_video_style_id` references `video_styles(id)`
  - `default_conversation_style_id` references `conversation_styles(id)`

#### `business_information`
- **Primary Key**: `id` (integer)
- **Key Fields**: `user_id`, `business_name`, `business_email`, `business_type`, `business_website`, `instagram_handle`, `linkedin_url`, `facebook_url`, `business_description`, `target_audience`, `created_at`, `updated_at`
- **Foreign Keys**: `user_id` references `users(id)` (with CASCADE delete)

### 3. Podcast Management

#### `podcasts`
- **Primary Key**: `id` (integer)
- **Key Fields**: `user_id`, `title`, `description`, `cover_image`, `language`, `audience_type`, `categories[]`, `keywords[]`, `website`, `email`, `contact_number`, `group_id`, `video_style_id`, `conversation_style_id`, `profile_type_id`, `speaker1_id`, `speaker2_id`, `created_at`, `updated_at`
- **Foreign Keys**:
  - `user_id` references `users(id)`
  - `group_id` references `podcast_groups(id)`
  - `video_style_id` references `video_styles(id)`
  - `conversation_style_id` references `conversation_styles(id)`
  - `profile_type_id` references `profile_types(id)`
  - `speaker1_id` references `speakers(id)`
  - `speaker2_id` references `speakers(id)`
- **Referenced By**: `episodes`, `podcast_platform_configs`

#### `podcast_groups`
- **Primary Key**: `id` (integer)
- **Key Fields**: `user_id`, `name`, `description`, `created_at`, `updated_at`
- **Foreign Keys**: `user_id` references `users(id)`
- **Referenced By**: `podcasts`

#### `episodes`
- **Primary Key**: `id` (integer)
- **Key Fields**: `podcast_id`, `title`, `description`, `duration`, `keywords[]`, `language`, `video_style_id`, `conversation_style_id`, `status`, `publish_date`, `cover_image`, `speaker1_id`, `speaker2_id`, `created_at`, `updated_at`
- **Foreign Keys**:
  - `podcast_id` references `podcasts(id)`
  - `video_style_id` references `video_styles(id)`
  - `conversation_style_id` references `conversation_styles(id)`
  - `speaker1_id` references `speakers(id)`
  - `speaker2_id` references `speakers(id)`
- **Referenced By**: `credit_usage`

#### `podcast_platform_configs`
- **Primary Key**: `id` (integer)
- **Key Fields**: `podcast_id`, `platform_id`, `enabled`, `auto_publish`, `account_id`, `created_at`, `updated_at`
- **Foreign Keys**:
  - `podcast_id` references `podcasts(id)`
  - `platform_id` references `platforms(id)`

### 4. Speakers and Voices

#### `speakers`
- **Primary Key**: `id` (integer)
- **Key Fields**: `user_id`, `name`, `profile_type_id`, `profile_url`, `bio`, `voice_id`, `social_twitter`, `social_linkedin`, `social_website`, `created_at`, `updated_at`
- **Foreign Keys**:
  - `user_id` references `users(id)`
  - `profile_type_id` references `profile_types(id)`
  - `voice_id` references `elevenlabs_voices(voice_id)`
- **Referenced By**: 
  - `podcasts` (as speaker1 and speaker2)
  - `episodes` (as speaker1 and speaker2)

#### `elevenlabs_voices`
- **Primary Key**: `voice_id` (text)
- **Key Fields**: `name`, `category`, `description`, `labels` (jsonb), `gender`, `accent`, `age`, `language`, `use_case`, `preview_url`, `settings` (jsonb)
- **Referenced By**:
  - `speakers`
  - `user_settings` (as default_voice1 and default_voice2)

### 5. Master Data

#### `elevenlabs_voices`
- **Primary Key**: `voice_id` (string)
- **Key Fields**: `name`, `category`, `description`, `gender`, `accent`, `age`, `language`, `use_case`, `preview_url`, `labels`, `settings`
- **Relationships**:
  - One-to-Many with `speakers`
  - Referenced in `user_settings`

#### `conversation_styles`
- **Primary Key**: `id` (integer)
- **Key Fields**: `name`, `description`, `created_at`, `updated_at`
- **Relationships**:
  - Referenced in podcast creation

#### `video_styles`
- **Primary Key**: `id` (integer)
- **Key Fields**: `name`, `description`, `created_at`, `updated_at`
- **Relationships**:
  - Referenced in video generation settings

#### `profile_types`
- **Primary Key**: `id` (integer)
- **Key Fields**: `name`, `description`, `created_at`, `updated_at`
- **Relationships**:
  - Referenced in user profile settings

#### `platforms`
- **Primary Key**: `id` (integer)
- **Key Fields**: `name`, `icon_url`, `created_at`, `updated_at`
- **Relationships**:
  - Referenced in podcast distribution settings

### 6. Podcast Jobs and Processing

#### `podcast_jobs`
- **Primary Key**: `id` (integer)
- **Key Fields**: `profile_name`, `customer_id`, `conversation_type`, `topic`, `status`, `error_message`, `audio_task_id`, `video_task_id`, `output_path`, `youtube_channel_id`, `youtube_playlist_id`, `created_at`, `updated_at`
- **Referenced By**: `episodes` (via job_id)

#### `video_paths`
- **Primary Key**: `id` (integer)
- **Key Fields**: `job_id`, `audio_path`, `welcome_audio_path`, `intro_video_path`, `bumper_video_path`, `short_video_path`, `main_video_path`, `outro_video_path`, `welcome_video_avatar_path`, `created_at`, `updated_at`

### 7. Payment and Subscription

#### `plans`
- **Primary Key**: `id` (integer)
- **Unique Fields**: `name`
- **Key Fields**: `description`, `price`, `credits`, `features` (jsonb), `is_active`, `created_at`, `updated_at`
- **Referenced By**: `subscriptions`

#### `subscriptions`
- **Primary Key**: `id` (integer)
- **Key Fields**: `user_id`, `plan_id`, `status`, `start_date`, `end_date`, `auto_renew`, `payment_method_id`, `external_subscription_id`, `created_at`, `updated_at`
- **Foreign Keys**:
  - `user_id` references `users(id)`
  - `plan_id` references `plans(id)`
- **Referenced By**: `transactions`

#### `transactions`
- **Primary Key**: `id` (integer)
- **Key Fields**: `user_id`, `subscription_id`, `amount`, `currency`, `status`, `payment_method`, `payment_processor`, `external_transaction_id`, `description`, `transaction_data` (jsonb), `created_at`
- **Foreign Keys**:
  - `user_id` references `users(id)`
  - `subscription_id` references `subscriptions(id)`

#### `payment_methods`
- **Primary Key**: `id` (integer)
- **Key Fields**: `user_id`, `type`, `provider`, `external_id`, `is_default`, `last_four`, `expiry_month`, `expiry_year`, `card_type`, `billing_details` (jsonb), `created_at`, `updated_at`
- **Foreign Keys**: `user_id` references `users(id)`

### 8. Credits System

#### `credits`
- **Primary Key**: `id` (integer)
- **Key Fields**: `user_id`, `amount`, `price`, `transaction_id`, `status`, `created_at`
- **Foreign Keys**: `user_id` references `users(id)`

#### `credit_usage`
- **Primary Key**: `id` (integer)
- **Key Fields**: `user_id`, `episode_id`, `credits_used`, `minutes_used`, `created_at`
- **Foreign Keys**:
  - `user_id` references `users(id)`
  - `episode_id` references `episodes(id)`

### 9. YouTube Integration

#### `customer_youtube_channels`
- **Primary Key**: `id` (integer)
- **Key Fields**: `channel_id`, `name`, `created_at`, `updated_at`
- **Referenced By**: `customer_youtube_playlists`

#### `customer_youtube_playlists`
- **Primary Key**: `id` (integer)
- **Key Fields**: `channel_id`, `playlist_id`, `playlist_title`, `playlist_description`, `is_default`, `created_at`, `updated_at`
- **Foreign Keys**: `channel_id` references `customer_youtube_channels(id)`

## Relationships Diagram

```
users
├── user_settings (1:1)
├── business_information (1:1)
├── podcasts (1:N)
├── podcast_groups (1:N)
├── speakers (1:N)
├── credits (1:N)
├── credit_usage (1:N)
├── subscriptions (1:N)
├── transactions (1:N)
├── payment_methods (1:N)
└── password_resets (1:N)

podcasts
├── episodes (1:N)
├── podcast_platform_configs (1:N)
└── references
    ├── users (N:1)
    ├── podcast_groups (N:1)
    ├── video_styles (N:1)
    ├── conversation_styles (N:1)
    ├── profile_types (N:1)
    ├── speakers (N:1) as speaker1
    └── speakers (N:1) as speaker2

episodes
├── credit_usage (1:N)
└── references
    ├── podcasts (N:1)
    ├── video_styles (N:1)
    ├── conversation_styles (N:1)
    ├── speakers (N:1) as speaker1
    └── speakers (N:1) as speaker2

speakers
├── references
│   ├── users (N:1)
│   ├── profile_types (N:1)
│   └── elevenlabs_voices (N:1)
└── referenced by
    ├── podcasts (as speaker1 and speaker2)
    └── episodes (as speaker1 and speaker2)

elevenlabs_voices
└── referenced by
    ├── speakers
    ├── user_settings (as default_voice1)
    └── user_settings (as default_voice2)
```

## Important Notes

1. The `users` table is the central entity with relationships to most other tables.
2. Speaker relationships are complex, with each podcast/episode having two potential speakers.
3. Voice settings use the ElevenLabs API, with voice data stored in the `elevenlabs_voices` table.
4. The credit system tracks usage per episode and user.
5. The platform supports multiple distribution channels through the `platforms` and `podcast_platform_configs` tables.
6. YouTube integration is handled through dedicated tables for channels and playlists.

This documentation provides a high-level overview of the database structure. For detailed field descriptions and constraints, refer to the actual database schema or the SQLAlchemy models in the codebase.
