#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/payment_coordinator.py
🎯 PURPOSE: Payment routes stub - minimal safe implementation
🔗 IMPORTS: FastAPI router
📤 EXPORTS: payment_router
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import hashlib
import hmac
import secrets
import re
import logging

from models import get_db
from models.subscription import Subscription
from config import config

try:
    import stripe
except Exception as _e:
    stripe = None
from dependencies.auth import get_current_user
from models.payment import Payment

# Configure logging
logger = logging.getLogger(__name__)

# Security configuration
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")  # Get from environment
ALLOWED_PAYMENT_METHODS = ["card", "bank_transfer"]
MAX_PAYMENT_AMOUNT_CENTS = 1000000  # $10,000 max
MIN_PAYMENT_AMOUNT_CENTS = 50  # $0.50 min
RATE_LIMIT_WINDOW = 300  # 5 minutes
MAX_ATTEMPTS_PER_WINDOW = 5

# Track payment attempts (in production, use Redis)
payment_attempts: Dict[str, list] = {}

# Security exceptions
class PaymentSecurityError(Exception):
    """Base payment security exception"""
    pass

class InvalidPaymentAmount(PaymentSecurityError):
    """Invalid payment amount"""
    pass

class RateLimitExceeded(PaymentSecurityError):
    """Too many payment attempts"""
    pass

class InvalidWebhookSignature(PaymentSecurityError):
    """Webhook signature verification failed"""
    pass

# Security helper functions
def validate_payment_amount(amount_cents: int) -> None:
    """Validate payment amount is within acceptable range"""
    if amount_cents < MIN_PAYMENT_AMOUNT_CENTS:
        raise InvalidPaymentAmount(
            f"Payment amount too small. Minimum: ${MIN_PAYMENT_AMOUNT_CENTS/100:.2f}"
        )
    if amount_cents > MAX_PAYMENT_AMOUNT_CENTS:
        raise InvalidPaymentAmount(
            f"Payment amount too large. Maximum: ${MAX_PAYMENT_AMOUNT_CENTS/100:.2f}"
        )

def check_rate_limit(user_email: str) -> None:
    """Check if user has exceeded payment attempt rate limit"""
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)
    
    # Clean old attempts
    if user_email in payment_attempts:
        payment_attempts[user_email] = [
            attempt for attempt in payment_attempts[user_email]
            if attempt > window_start
        ]
    
    # Check current window
    attempts = payment_attempts.get(user_email, [])
    if len(attempts) >= MAX_ATTEMPTS_PER_WINDOW:
        logger.warning(f"Rate limit exceeded for user: {user_email}")
        raise RateLimitExceeded(
            f"Too many payment attempts. Please try again in {RATE_LIMIT_WINDOW//60} minutes."
        )
    
    # Record this attempt
    if user_email not in payment_attempts:
        payment_attempts[user_email] = []
    payment_attempts[user_email].append(now)

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature. Prefer Stripe verification when configured."""
    # Use Stripe verification when possible
    if stripe and secret and signature:
        try:
            # Stripe raises if invalid
            stripe.Webhook.construct_event(payload=payload, sig_header=signature, secret=secret)
            return True
        except Exception:
            return False
    # Fallback to HMAC if Stripe not available
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)

def generate_idempotency_key() -> str:
    """Generate unique idempotency key for payment requests"""
    return secrets.token_urlsafe(32)

def sanitize_card_number(card_number: str) -> str:
    """Mask card number for logging (show only last 4 digits)"""
    if len(card_number) < 4:
        return "****"
    return "*" * (len(card_number) - 4) + card_number[-4:]

# Create router
payment_router = APIRouter(
    prefix="/api/payments",
    tags=["Payments"],
    responses={404: {"description": "Not found"}},
)

# Request models with security validation
class CheckoutRequest(BaseModel):
    plan: str = Field(default="standard", pattern="^(free|standard|premium|enterprise)$")
    payment_method: str = Field(..., pattern="^(card|bank_transfer)$")
    amount_cents: int = Field(..., gt=0)
    currency: str = Field(default="USD", pattern="^[A-Z]{3}$")
    
    @validator('amount_cents')
    def validate_amount(cls, v):
        """
        Validate payment amount is within allowed range.
        
        Args:
            v: The amount in cents to validate
            
        Returns:
            int: The validated amount
            
        Raises:
            ValueError: If amount is outside allowed range
        """
        validate_payment_amount(v)
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        """
        Validate payment method is supported.
        
        Args:
            v: The payment method to validate
            
        Returns:
            str: The validated payment method
            
        Raises:
            ValueError: If payment method is not in allowed list
        """
        if v not in ALLOWED_PAYMENT_METHODS:
            raise ValueError(f"Invalid payment method. Allowed: {ALLOWED_PAYMENT_METHODS}")
        return v
    
class SubscriptionUpdate(BaseModel):
    action: str = Field(..., pattern="^(cancel|update|pause|resume)$")
    new_plan: Optional[str] = Field(None, pattern="^(free|standard|premium|enterprise)$")
    reason: Optional[str] = Field(None, max_length=500)
    
class PaymentWebhook(BaseModel):
    event_type: str
    payment_id: str
    timestamp: datetime
    data: Dict[str, Any]

@payment_router.post("/checkout")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create checkout session with comprehensive security checks"""
    try:
        # Rate limiting
        check_rate_limit(current_user)
        
        # Log payment attempt (without sensitive data)
        logger.info(f"Payment attempt by {current_user} for plan {request.plan}")
        
        # Generate idempotency key to prevent duplicate charges
        idempotency_key = generate_idempotency_key()
        
        # Additional validation
        if request.amount_cents <= 0:
            raise InvalidPaymentAmount("Invalid payment amount")
        
        # Guarded Stripe checkout implementation
        if stripe and config.STRIPE_API_KEY:
            stripe.api_key = config.STRIPE_API_KEY
            try:
                # Create or get Stripe customer
                if not current_user.stripe_customer_id:
                    customer = stripe.Customer.create(email=current_user)
                    current_user.stripe_customer_id = customer.id
                    db.commit()
                customer_id = current_user.stripe_customer_id
                session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{
                        "price_data": {
                            "currency": request.currency.lower(),
                            "product_data": {"name": f"CORA {request.plan.capitalize()}"},
                            "unit_amount": request.amount_cents,
                        },
                        "quantity": 1,
                    }],
                    mode="payment",
                    success_url=f"{config.BASE_URL}/subscription?status=success&session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=f"{config.BASE_URL}/pricing?checkout=cancelled",
                    metadata={
                        "plan": request.plan,
                        "user": current_user,
                    },
                    idempotency_key=idempotency_key
                )
                
                # Create Payment record
                payment = Payment(
                    customer_id=customer_id,
                    amount=request.amount_cents / 100.0,
                    currency=request.currency,
                    status="pending",
                    stripe_payment_intent_id=session.payment_intent
                )
                db.add(payment)
                db.commit()
                
                return {
                    "checkout_session_id": session.id,
                    "checkout_url": session.url,
                    "idempotency_key": idempotency_key,
                    "plan": request.plan,
                    "amount": f"${request.amount_cents/100:.2f}",
                    "currency": request.currency,
                    "status": "created"
                }
            except stripe.error.StripeError as e:
                logger.error(f"Stripe error: {str(e)}")
                raise HTTPException(status_code=500, detail="Payment processing failed")
        else:
            # Secure stub response when Stripe not configured
            return {
                "checkout_session_id": f"cs_test_{secrets.token_urlsafe(16)}",
                "idempotency_key": idempotency_key,
                "plan": request.plan,
                "amount": f"${request.amount_cents/100:.2f}",
                "currency": request.currency,
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "status": "pending"
            }
        
    except RateLimitExceeded as e:
        raise HTTPException(status_code=429, detail=str(e))
    except InvalidPaymentAmount as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PaymentSecurityError as e:
        logger.error(f"Payment security error: {str(e)}")
        raise HTTPException(status_code=400, detail="Payment validation failed")
    except Exception as e:
        logger.error(f"Unexpected payment error: {str(e)}")
        raise HTTPException(status_code=500, detail="Payment processing failed")

# Implement subscription lookup
@payment_router.get("/subscription")
async def get_subscription(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = db.query(Subscription).filter(
        Subscription.user_email == current_user,
        Subscription.status == "active"
    ).first()
    
    if not sub:
        return {
            "status": "inactive",
            "message": "No active subscription found"
        }
    
    return {
        "plan_name": sub.plan_name,
        "status": sub.status,
        "current_period_start": sub.current_period_start,
        "current_period_end": sub.current_period_end,
        "stripe_subscription_id": sub.stripe_subscription_id
    }

# Pydantic model for trial creation
class TrialRequest(BaseModel):
    plan: str = Field(..., pattern="^(SOLO|CREW|BUSINESS)$", description="Plan name: SOLO, CREW, or BUSINESS")

@payment_router.post("/subscriptions/create-trial")
async def create_trial_subscription(
    request: TrialRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a trial subscription for the current user"""
    try:
        user_email = current_user.email if hasattr(current_user, 'email') else str(current_user)
        
        # Check if user already has a subscription
        existing_sub = db.query(Subscription).filter(Subscription.user_email == user_email).first()
        if existing_sub:
            return {
                "success": False,
                "message": "User already has an active subscription"
            }
        
        # Plan pricing mapping
        plan_prices = {
            "SOLO": 49.00,
            "CREW": 99.00,
            "BUSINESS": 199.00
        }
        
        plan_name = request.plan.upper()
        plan_price = plan_prices.get(plan_name, 49.00)
        
        # Create subscription record
        subscription = Subscription(
            user_email=user_email,
            plan_name=plan_name,
            status="trialing",
            current_period_start=datetime.utcnow(),
            current_period_end=datetime.utcnow() + timedelta(days=30),  # 30-day trial
        )
        
        # Try Stripe integration if available
        if stripe and config.STRIPE_API_KEY:
            try:
                stripe.api_key = config.STRIPE_API_KEY
                
                # Create Stripe customer
                customer = stripe.Customer.create(
                    email=user_email,
                    metadata={"plan": plan_name, "trial_user": "true"}
                )
                
                # Get price ID for the plan
                price_ids = {
                    "SOLO": getattr(config, 'STRIPE_STARTER_PRICE_ID', None),
                    "CREW": getattr(config, 'STRIPE_PROFESSIONAL_PRICE_ID', None),
                    "BUSINESS": getattr(config, 'STRIPE_ENTERPRISE_PRICE_ID', None)
                }
                
                price_id = price_ids.get(plan_name)
                
                if price_id:
                    # Create trial subscription in Stripe
                    stripe_subscription = stripe.Subscription.create(
                        customer=customer.id,
                        items=[{"price": price_id}],
                        trial_period_days=30,
                        metadata={
                            "plan": plan_name,
                            "user_email": user_email
                        }
                    )
                    
                    # Update subscription with Stripe data
                    subscription.stripe_subscription_id = stripe_subscription.id
                    logger.info(f"Created Stripe trial subscription for {user_email}: {stripe_subscription.id}")
                
            except Exception as stripe_error:
                logger.warning(f"Stripe trial creation failed for {user_email}: {stripe_error}")
                # Continue without Stripe - local trial only
        
        # Save subscription to database
        db.add(subscription)
        db.commit()
        
        logger.info(f"Trial subscription created for {user_email}: {plan_name}")
        
        return {
            "success": True,
            "message": f"Trial started successfully for {plan_name} plan",
            "plan": plan_name,
            "trial_end": subscription.current_period_end.isoformat(),
            "stripe_enabled": bool(subscription.stripe_subscription_id)
        }
        
    except Exception as e:
        logger.error(f"Trial creation failed: {e}")
        return {
            "success": False,
            "message": f"Failed to create trial: {str(e)}"
        }

@payment_router.post("/subscription")
async def update_subscription(
    request: SubscriptionUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        sub = db.query(Subscription).filter(
            Subscription.user_email == current_user,
            Subscription.status.in_(["active", "paused"])
        ).first()
        
        if not sub:
            raise HTTPException(status_code=404, detail="No active subscription found")
        
        if stripe and config.STRIPE_API_KEY:
            stripe.api_key = config.STRIPE_API_KEY
            
            if request.action == "cancel":
                stripe.Subscription.delete(sub.stripe_subscription_id)
                sub.status = "canceled"
                sub.canceled_at = datetime.utcnow()
            elif request.action == "update" and request.new_plan:
                stripe.Subscription.modify(
                    sub.stripe_subscription_id,
                    items=[{"id": sub.stripe_subscription_id, "plan": request.new_plan}]
                )
                sub.plan_name = request.new_plan
            elif request.action == "pause":
                stripe.Subscription.modify(sub.stripe_subscription_id, pause_collection={"behavior": "void"})
                sub.status = "paused"
            elif request.action == "resume":
                stripe.Subscription.modify(sub.stripe_subscription_id, pause_collection=None)
                sub.status = "active"
            else:
                raise HTTPException(status_code=400, detail="Invalid action")
            
            db.commit()
            return {"action": request.action, "status": "success", "subscription": sub.__dict__}
        else:
            # Stub for no Stripe
            sub.status = request.action if request.action in ["canceled", "paused", "active"] else sub.status
            sub.plan_name = request.new_plan or sub.plan_name
            db.commit()
            return {"action": request.action, "status": "pending", "message": "Stripe not configured"}
    
    except Exception as e:
        logger.error(f"Subscription update failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Subscription update failed")

@payment_router.post("/webhook")
async def payment_webhook(
    request: Request,
    webhook_data: PaymentWebhook,
    db: Session = Depends(get_db)
):
    """Handle payment provider webhooks with signature verification"""
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Prefer Stripe signature header when configured
        signature = request.headers.get("Stripe-Signature") or request.headers.get("X-Webhook-Signature", "")
        
        # Verify webhook signature
        if not verify_webhook_signature(body, signature, WEBHOOK_SECRET):
            logger.error("Invalid webhook signature")
            raise InvalidWebhookSignature("Webhook signature verification failed")
        
        # Attempt to parse Stripe event if available
        event_type = webhook_data.event_type
        event = None
        if stripe and signature and WEBHOOK_SECRET:
            try:
                event = stripe.Webhook.construct_event(payload=body, sig_header=signature, secret=WEBHOOK_SECRET)
                event_type = event.get("type", event_type)
            except Exception as e:
                logger.warning(f"Stripe event parsing failed, using payload type: {e}")
        
        # Log webhook (without sensitive data)
        logger.info(f"Webhook received: {event_type} for payment {webhook_data.payment_id}")
        
        # Process based on event type
        if event_type in ("payment_intent.succeeded", "checkout.session.completed", "invoice.payment_succeeded"):
            # Update user subscription status
            sub_data = event['data']['object']
            sub = db.query(Subscription).filter(Subscription.user_email == sub_data.get('customer_email')).first()
            if not sub:
                sub = Subscription(user_email=sub_data.get('customer_email'))
                db.add(sub)
            sub.status = "active"
            sub.plan_name = sub_data.get('plan', 'standard')
            sub.current_period_start = datetime.fromtimestamp(sub_data['current_period_start'])
            sub.current_period_end = datetime.fromtimestamp(sub_data['current_period_end'])
            sub.stripe_subscription_id = sub_data['id']
            db.commit()
        
        elif event_type in ("payment_intent.payment_failed", "invoice.payment_failed"):
            logger.warning(f"Payment failed: {webhook_data.payment_id}")
            payment_id = webhook_data.data.get("payment_id")
            # Update payment status in DB to 'failed'
            payment = db.query(Payment).filter(Payment.stripe_payment_intent_id == payment_id).first()
            if payment:
                payment.status = "failed"
                db.commit()
        
        elif event_type in ("customer.subscription.deleted", "customer.subscription.cancelled"):
            logger.info(f"Subscription cancelled: {webhook_data.payment_id}")
            sub_id = webhook_data.data.get("subscription_id")
            sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == sub_id).first()
            if sub:
                sub.status = "canceled"
                sub.canceled_at = datetime.utcnow()
                db.commit()
        
        # Always return 200 to acknowledge receipt
        return {"status": "received"}
        
    except InvalidWebhookSignature as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        # Still return 200 to prevent retries for processing errors
        return {"status": "error", "message": "Processing failed"}