"""
Purpose and Objective: 
This module defines Pydantic schemas for credit-related API endpoints including
credit purchases, usage tracking, and balance reporting.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .base import BaseSchema

# Credit schemas
class CreditBase(BaseSchema):
    """Base schema for credits"""
    amount: int = Field(..., example=100)
    price: float = Field(..., example=9.99)
    transaction_id: Optional[str] = Field(None, example="txn_123456789")
    status: str = Field("pending", example="completed")

class CreditCreate(CreditBase):
    """Schema for creating credits"""
    pass

class CreditResponse(CreditBase):
    """Schema for credit response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")

# Credit Usage schemas
class CreditUsageBase(BaseSchema):
    """Base schema for credit usage"""
    episode_id: int = Field(..., example=1)
    credits_used: int = Field(..., example=10)
    minutes_used: int = Field(..., example=30)

class CreditUsageCreate(CreditUsageBase):
    """Schema for creating credit usage records"""
    pass

class CreditUsageResponse(CreditUsageBase):
    """Schema for credit usage response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")

# Credit Balance schemas
class CreditBalanceResponse(BaseSchema):
    """Schema for credit balance response"""
    user_id: int = Field(..., example=1)
    total_credits: int = Field(..., example=500)
    used_credits: int = Field(..., example=150)
    remaining_credits: int = Field(..., example=350)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "total_credits": 500,
                "used_credits": 150,
                "remaining_credits": 350
            }
        }

# Credit History schemas
class CreditHistoryItem(BaseSchema):
    """Schema for credit history item"""
    id: int = Field(..., example=1)
    type: str = Field(..., example="purchase")  # purchase, usage, refund, etc.
    amount: int = Field(..., example=100)
    description: str = Field(..., example="Purchased 100 credits")
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    # Optional related data
    episode_id: Optional[int] = Field(None, example=1)
    transaction_id: Optional[str] = Field(None, example="txn_123456789")

class CreditHistoryResponse(BaseSchema):
    """Schema for credit history response"""
    items: List[CreditHistoryItem]
    total_items: int = Field(..., example=10)
