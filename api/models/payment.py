"""
Purpose and Objective: 
This module defines SQLAlchemy models for payment-related entities including
Plan, Subscription, Transaction, and PaymentMethod. These models represent
the payment and subscription system for the podcast platform.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from ..db import Base

class Plan(Base):
    """
    SQLAlchemy model for subscription plans.
    Defines different pricing tiers and included features.
    """
    __tablename__ = "plans"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)
    price = Column(Float)
    credits = Column(Integer)
    features = Column(JSONB)  # Store features as a JSON array
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")

class Subscription(Base):
    """
    SQLAlchemy model for user subscriptions.
    Tracks active subscriptions and their status.
    """
    __tablename__ = "subscriptions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    plan_id = Column(Integer, ForeignKey("plans.id"))
    status = Column(String)  # active, canceled, expired, etc.
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    payment_method_id = Column(String, nullable=True)
    external_subscription_id = Column(String, nullable=True)  # For payment processor reference
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    transactions = relationship("Transaction", back_populates="subscription")

class Transaction(Base):
    """
    SQLAlchemy model for payment transactions.
    Records all financial transactions in the system.
    """
    __tablename__ = "transactions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    amount = Column(Float)
    currency = Column(String, default="USD")
    status = Column(String)  # completed, pending, failed, refunded
    payment_method = Column(String)  # credit_card, paypal, etc.
    payment_processor = Column(String)  # stripe, paypal, etc.
    external_transaction_id = Column(String, nullable=True)  # For payment processor reference
    description = Column(Text)
    transaction_data = Column(JSONB, nullable=True)  # Additional transaction data
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")
    subscription = relationship("Subscription", back_populates="transactions")

class PaymentMethod(Base):
    """
    SQLAlchemy model for user payment methods.
    Stores payment method information for users.
    """
    __tablename__ = "payment_methods"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # credit_card, paypal, etc.
    provider = Column(String)  # stripe, paypal, etc.
    external_id = Column(String)  # Payment processor's ID for this method
    is_default = Column(Boolean, default=False)
    last_four = Column(String, nullable=True)  # Last 4 digits of card
    expiry_month = Column(Integer, nullable=True)
    expiry_year = Column(Integer, nullable=True)
    card_type = Column(String, nullable=True)  # visa, mastercard, etc.
    billing_details = Column(JSONB, nullable=True)  # Billing address, name, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payment_methods")
