#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/payments.py
🎯 PURPOSE: Payment and subscription management routes
🔗 IMPORTS: FastAPI, models, services
📤 EXPORTS: payment_router
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from models import get_db, Payment, Customer, Subscription

# Create router
payment_router = APIRouter(
    prefix="/api/payments",
    tags=["payments"]
)

# Pydantic models
class PaymentResponse(BaseModel):
    id: int
    customer_id: int
    amount: float
    currency: str
    status: str
    stripe_payment_intent_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class CustomerResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    stripe_customer_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    id: int
    customer_id: int
    plan_name: str
    price: float
    status: str
    stripe_subscription_id: str
    current_period_start: datetime
    current_period_end: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Routes
@payment_router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all customers"""
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return customers

@payment_router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get a specific customer"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@payment_router.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all subscriptions, optionally filtered by status"""
    query = db.query(Subscription)
    if status:
        query = query.filter(Subscription.status == status)
    subscriptions = query.offset(skip).limit(limit).all()
    return subscriptions

@payment_router.get("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    """Get a specific subscription"""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

@payment_router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    customer_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all payments, optionally filtered by customer or status"""
    query = db.query(Payment)
    if customer_id:
        query = query.filter(Payment.customer_id == customer_id)
    if status:
        query = query.filter(Payment.status == status)
    payments = query.offset(skip).limit(limit).all()
    return payments

@payment_router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, db: Session = Depends(get_db)):
    """Get a specific payment"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment