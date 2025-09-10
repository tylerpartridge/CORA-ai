<!-- CI: Smoke workflow badge -->
[![Smoke](https://github.com/tylerpartridge/CORA-ai/actions/workflows/smoke.yml/badge.svg)](https://github.com/tylerpartridge/CORA-ai/actions/workflows/smoke.yml)

# CORA - Your AI Business Brain

CORA is more than bookkeeping. She's your complete AI business advisor - handling everything from financial planning to legal compliance, built natively for the AI-to-AI economy.

## 🚀 Quick Start

**Requirements:** Python 3.12 (not 3.13+)

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r data/requirements.txt

# Start CORA
python app.py
## CI Actions Links
- Smoke: https://github.com/tylerpartridge/CORA-ai/actions/workflows/smoke.yml
- Uptime Sync: https://github.com/tylerpartridge/CORA-ai/actions/workflows/uptime-sync.yml
- Monitoring Postcheck: https://github.com/tylerpartridge/CORA-ai/actions/workflows/monitoring-postcheck.yml
```

### Quick Start (Local)

```bash
python -m uvicorn app:app --reload
BASE=http://127.0.0.1:8000 python tools/smoke_http.py
```

## 🧠 What CORA Does

- **Business Planning** - Strategic advisor who understands your goals
- **Financial Advisory** - Investment strategies, cash flow optimization  
- **Tax Planning** - Proactive tax strategy, not just filing
- **Bookkeeping** - Yes, she does this too, brilliantly
- **Legal Advisory** - Business structure, compliance, contracts
- **AI Integration** - Native compatibility with all AI systems

## 🏗️ Architecture

Built with simplicity and scale in mind:
- FastAPI backend
- Clean 5-file root structure
- AI-first API design
- Human-AI collaborative workspace (.mind/)

## 💳 Stripe Payment Configuration

CORA supports Stripe Payment Links for subscription CTAs on the pricing page.

### Environment Variables

Configure these in your `.env` file:

```bash
# Generic payment link (applies to all plans if specific ones aren't set)
PAYMENT_LINK=https://buy.stripe.com/your_generic_payment_link

# Plan-specific payment links (optional, override generic)
PAYMENT_LINK_SOLO=https://buy.stripe.com/your_solo_plan_link
PAYMENT_LINK_CREW=https://buy.stripe.com/your_crew_plan_link
PAYMENT_LINK_BUSINESS=https://buy.stripe.com/your_business_plan_link
```

### Fallback Behavior

- If payment links are configured, CTAs will open Stripe Payment Links in a new tab
- If no payment links are set, CTAs fallback to `/signup?plan=PLANNAME`
- Plan-specific links override the generic PAYMENT_LINK

## 📞 Contact

Visit [coraai.tech](https://coraai.tech) to learn more.

---
*Version 4.0 - Built for the AI economy*
![CI](https://github.com/tylerpartridge/CORA-ai/actions/workflows/ci.yml/badge.svg)
