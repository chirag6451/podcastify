"""
Purpose and Objective: 
This module defines Pydantic schemas for payment-related API endpoints including
plans, subscriptions, transactions, and payment methods.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseSchema

# Plan schemas
class PlanBase(BaseSchema):
    """Base schema for subscription plans"""
    name: str = Field(..., example="Pro Plan")
    description: str = Field(..., example="Professional plan with advanced features")
    price: float = Field(..., example=29.99)
    credits: int = Field(..., example=500)
    features: Dict[str, Any] = Field(..., example={
        "max_episodes": 50,
        "video_export": True,
        "priority_processing": True
    })
    is_active: bool = Field(True, example=True)

class PlanCreate(PlanBase):
    """Schema for creating plans"""
    pass

class PlanResponse(PlanBase):
    """Schema for plan response"""
    id: int = Field(..., example=1)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")

# Subscription schemas
class SubscriptionBase(BaseSchema):
    """Base schema for subscriptions"""
    plan_id: int = Field(..., example=1)
    status: str = Field(..., example="active")
    auto_renew: bool = Field(True, example=True)
    payment_method_id: Optional[str] = Field(None, example="pm_123456789")

class SubscriptionCreate(SubscriptionBase):
    """Schema for creating subscriptions"""
    pass

class SubscriptionResponse(SubscriptionBase):
    """Schema for subscription response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    start_date: datetime = Field(..., example="2025-04-24T12:00:00Z")
    end_date: Optional[datetime] = Field(None, example="2026-04-24T12:00:00Z")
    external_subscription_id: Optional[str] = Field(None, example="sub_123456789")
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    
    # Nested plan data
    plan: Optional[PlanResponse] = None

# Transaction schemas
class TransactionBase(BaseSchema):
    """Base schema for transactions"""
    amount: float = Field(..., example=29.99)
    currency: str = Field("USD", example="USD")
    status: str = Field(..., example="completed")
    payment_method: str = Field(..., example="credit_card")
    payment_processor: str = Field(..., example="stripe")
    description: str = Field(..., example="Monthly subscription payment")

class TransactionCreate(TransactionBase):
    """Schema for creating transactions"""
    subscription_id: Optional[int] = Field(None, example=1)
    external_transaction_id: Optional[str] = Field(None, example="txn_123456789")
    transaction_data: Optional[Dict[str, Any]] = Field(None)

class TransactionResponse(TransactionBase):
    """Schema for transaction response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    subscription_id: Optional[int] = Field(None, example=1)
    external_transaction_id: Optional[str] = Field(None, example="txn_123456789")
    transaction_data: Optional[Dict[str, Any]] = Field(None)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")

# Payment Method schemas
class PaymentMethodBase(BaseSchema):
    """Base schema for payment methods"""
    type: str = Field(..., example="credit_card")
    provider: str = Field(..., example="stripe")
    external_id: str = Field(..., example="pm_123456789")
    is_default: bool = Field(False, example=True)
    last_four: Optional[str] = Field(None, example="4242")
    expiry_month: Optional[int] = Field(None, example=12)
    expiry_year: Optional[int] = Field(None, example=2025)
    card_type: Optional[str] = Field(None, example="visa")

class PaymentMethodCreate(PaymentMethodBase):
    """Schema for creating payment methods"""
    billing_details: Optional[Dict[str, Any]] = Field(None, example={
        "name": "John Doe",
        "address": {
            "line1": "123 Main St",
            "city": "San Francisco",
            "state": "CA",
            "postal_code": "94111",
            "country": "US"
        }
    })

class PaymentMethodResponse(PaymentMethodBase):
    """Schema for payment method response"""
    id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    billing_details: Optional[Dict[str, Any]] = Field(None)
    created_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
    updated_at: datetime = Field(..., example="2025-04-24T12:00:00Z")
