# Card: GITHUB_SECRET_BLOCKING_SOLUTION.md

> Source: `docs\ai-awareness\GITHUB_SECRET_BLOCKING_SOLUTION.md`

## Headers:
- # GitHub Secret Scanning Block - Solution
- ## The Problem:
- ## Quick Solutions:
- ### Option 1: Allow the secrets (Fastest)
- ### Option 2: Clean commit (More secure)

## Content:
GitHub is blocking the push because it detected API keys in these files: - `DNS_CONFIGURATION_GUIDE.md` (SendGrid API Key) - `SONNET_DNS_HANDOFF.md` (SendGrid API Key)  - `docs/BOOTUP_SMOKE_TESTS.md` (Stripe API Keys) Click these GitHub links to allow the secrets: - SendGrid: https://github.com/tylerpartridge/CORA-ai/security/secret-scanning/unblock-secret/31dsb4Nj0hYQkDXC1UtM36FsJCX - Stripe 1: https://github.com/tylerpartridge/CORA-ai/security/secret-scanning/unblock-secret/31dsazQM5z8gVlFBQ326pdkJtA4 - Stripe 2: https://github.com/tylerpartridge/CORA-ai/security/secret-scanning/unblock-secret/31dsb0iqMXgTjTdBJ4xfJTqbSKY Then run: ```bash...
