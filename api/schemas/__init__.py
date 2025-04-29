"""
Purpose and Objective: 
This module re-exports all Pydantic schemas from domain-specific schema files to provide 
a clean import interface. This allows importing schemas directly from api.schemas
while maintaining a modular, domain-based file organization.
"""

# Base schemas
from .base import BaseSchema, MessageResponse, ErrorResponse, PaginatedResponse, DateTimeRange

# User schemas
from .user import (
    UserCreate, UserResponse, UserLogin, UserProfileUpdate,
    BusinessInformationCreate, BusinessInformationResponse,
    UserSettingsResponse, UserSettingsUpdate,
    ChangePassword, PasswordResetRequest, PasswordReset,
    Token, TokenData, CreditBalance
)

# Podcast schemas
from .podcast import (
    PodcastCreate, PodcastResponse, PodcastUpdate,
    EpisodeCreate, EpisodeResponse, EpisodeUpdate,
    PodcastGroupCreate, PodcastGroupResponse,
    PlatformConfigBase, PlatformConfigCreate, PlatformConfigResponse
)

# Voice schemas
from .voice import VoiceResponse, VoiceBase, VoiceFilter

# Style schemas
from .style import (
    ConversationStyleCreate, ConversationStyleResponse,
    VideoStyleCreate, VideoStyleResponse,
    ProfileTypeCreate, ProfileTypeResponse,
    PlatformCreate, PlatformResponse
)

# Speaker schemas
from .speaker import SpeakerCreate, SpeakerResponse, SpeakerUpdate

# Payment schemas
from .payment import (
    PlanCreate, PlanResponse,
    SubscriptionCreate, SubscriptionResponse,
    TransactionCreate, TransactionResponse,
    PaymentMethodCreate, PaymentMethodResponse
)

# Credit schemas
from .credit import (
    CreditCreate, CreditResponse,
    CreditUsageCreate, CreditUsageResponse,
    CreditBalanceResponse, CreditHistoryItem, CreditHistoryResponse
)

# Podcast job schemas
from .podcast_job import (
    PodcastJobCreate, PodcastJobResponse, PodcastJobUpdate
)

# Integration schemas
from .integration import (
    YouTubeChannelCreate, YouTubeChannelResponse,
    YouTubePlaylistCreate, YouTubePlaylistResponse,
    VideoPathCreate, VideoPathResponse, VideoPathUpdate
)
