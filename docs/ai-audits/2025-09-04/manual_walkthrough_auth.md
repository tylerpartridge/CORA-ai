# Manual Walkthrough — Section 1: Auth & Session

Date: 2025-09-04
Owner: QA — Manual Audit
Scope: User authentication, verification, session persistence, and account settings

## Preconditions
- Test user email available (e.g., tester+auth@coraai.tech)
- Access to staging/prod web app (`coraai.tech`) and email inbox for verification links
- Browser: Chrome latest (desktop + mobile emulation)

## Evidence Capture
- For each step: attach screenshots, response snippets, and timestamps
- Save artifacts under `docs/ai-audits/2025-09-04/evidence/auth/<case_id>/`

---

## A1. Registration
Steps:
1) Navigate to /signup
2) Complete form with valid inputs
3) Submit and observe confirmation

Expected:
- 200 OK flow; “verify email” prompt displayed
- Verification email sent from configured sender

Evidence:
- Screenshot: signup success
- Email headers + body (redact tokens)

Acceptance Criteria:
- New account is created and pending verification state is set

---

## A2. Email Verification
Steps:
1) Open verification email
2) Click verification link

Expected:
- Redirect to app; account marked verified
- Success banner/toast displayed

Evidence:
- Screenshot: verified state
- Network log: 200 from verify endpoint

Acceptance Criteria:
- Subsequent logins require no additional verification

---

## A3. Login (Verified User)
Steps:
1) Go to /login
2) Enter valid credentials
3) Submit

Expected:
- Redirect to dashboard or last-intended route
- Auth cookie/session/JWT stored; CSRF set (if applicable)

Evidence:
- Screenshot: landing post-login
- Storage/cookie snapshot

Acceptance Criteria:
- Login succeeds within <2s; no console errors

---

## A4. Session Persistence (7+ Days)
Steps:
1) Log in
2) Close browser; reopen after simulated time advance (devtools)
3) Revisit app without re-auth

Expected:
- Session persists beyond 7 days per requirement

Evidence:
- Cookie/session expiry values
- Access without re-login

Acceptance Criteria:
- Active session remains valid for required duration

---

## A5. Password Reset
Steps:
1) From /login, click “Forgot password”
2) Submit email; open reset email
3) Set new password; login with new password

Expected:
- Reset email delivered; token accepted once
- Old password invalid after reset

Evidence:
- Email body + headers (redact token)
- Screenshot: success confirmation

Acceptance Criteria:
- New password works; old does not

---

## A6. Rate Limiting (Auth Endpoints)
Steps:
1) Rapidly submit >N login attempts with wrong password
2) Observe throttling response

Expected:
- 429 responses after threshold; retry-after header present

Evidence:
- Network log with 429s and headers

Acceptance Criteria:
- Limits enforced without affecting normal users

---

## A7. Remember Me
Steps:
1) Check “Remember me” during login
2) Confirm extended expiry vs. normal login

Expected:
- Longer-lived session/cookie applied

Evidence:
- Cookie attributes (Expires/Max-Age)

Acceptance Criteria:
- Expiry matches product spec for remembered sessions

---

## A8. Timezone Selection
Steps:
1) Set timezone in profile/settings
2) View dates/times across dashboard and exports

Expected:
- All times reflect selected timezone

Evidence:
- Screenshots: settings + UI with expected times

Acceptance Criteria:
- No UTC/local mismatches; exports are timezone-correct

---

## A9. Currency Setting
Steps:
1) Set currency to non-USD in profile (if supported)
2) Validate display across expenses and reports

Expected:
- Currency symbol/format updates throughout UI

Evidence:
- Screenshots: expense list, detail, report

Acceptance Criteria:
- Consistent currency formatting across app

---

## A10. Logout
Steps:
1) Click logout from menu
2) Attempt to access protected route

Expected:
- Session cleared; redirected to login or 401/403

Evidence:
- Storage/cookie cleared
- Protected route response

Acceptance Criteria:
- No residual auth; must re-login to access protected routes

---

## Notes & Follow-ups
- Record any inconsistencies in `docs/ai-awareness/DECISIONS.md`
- If critical defects found, open P0 issue and link evidence
# Manual Walkthrough — Section 1: Auth & Session

- **Date**: 2025-09-04 (America/St_Johns)
- **Scope**: Authentication + Session lifecycle only (UI + API)
- **Acceptance** (must meet all):
  1) Email/password login works (happy path)
  2) Email verification flow redirects correctly (if enabled)
  3) Session persists across browser restarts (target ≥7 days)
  4) Password reset flow completes and logs in with new password
  5) Rate limiting returns correct status when abused (no crash)
  6) "Remember me" respected
  7) Timezone & currency preferences persist after login
  8) Protected routes return 401 when unauthenticated; 200 when authenticated
  9) /api/status returns 200 throughout

## 0) Test Matrix & Environment

- **Host(s)**:
  - PROD UI: https://coraai.tech/
  - PROD API: https://coraai.tech/api
  - LOCAL UI: http://localhost:8000/
  - LOCAL API: http://localhost:8000/api
  
- **Test Accounts** (create as needed):
  - A) fresh_user+auth1@example.com
  - B) reset_user+auth2@example.com
  
- **Browsers/Devices**: [desktop Chrome], [mobile Safari/Android]
- **Evidence Folder**: docs/ai-audits/2025-09-04/evidence/

## 1) Health & Baseline

- **Purpose**: Confirm service & schema are healthy before auth
- **Steps (API)**:
  ```bash
  curl -i https://coraai.tech/api/status
  curl -i https://coraai.tech/health
  ```
- **Expected**: HTTP/200 JSON; no 5xx
- **Evidence**:
  ```
  [Paste curl response headers/body here]
  ```

## 2) Signup → Email Verify → First Login

- **Purpose**: New user flow establishes session
- **UI Steps**:
  1. Visit `/signup`
  2. Enter email: `fresh_user+auth1@example.com`
  3. Enter password (8+ chars)
  4. Select timezone from dropdown
  5. Select currency (default USD)
  6. Submit form
  7. Check inbox for verification email
  8. Click verification link
  9. Confirm auto-redirect to dashboard or login
  
- **API (optional verification)**:
  ```bash
  curl -i -X POST https://coraai.tech/api/auth/register \
    -H "Content-Type: application/json" \
    -d '{"email":"fresh_user+auth1@example.com","password":"TestPass123!","timezone":"America/St_Johns","currency":"USD"}'
  ```
  
- **Expected**:
  - Account created with 201 status
  - Verification email sent
  - Redirect to dashboard post-verification
  
- **Evidence**:
  ```
  [Registration response]
  [Email screenshot]
  [Redirect URL captured]
  ```

## 3) Login (Happy Path) + Protected Route

- **Purpose**: Establish authenticated session and confirm guard behavior
- **Steps (UI)**: 
  1. Visit `/login`
  2. Enter verified account credentials
  3. Check "Remember me" option
  4. Submit
  
- **Steps (API)**:
  ```bash
  # Login attempt
  curl -i -X POST https://coraai.tech/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"fresh_user+auth1@example.com","password":"TestPass123!","remember_me":true}' \
    -c cookies.txt
  
  # Test protected route WITHOUT auth
  curl -i https://coraai.tech/api/me
  
  # Test protected route WITH auth
  curl -i https://coraai.tech/api/me -b cookies.txt
  ```
  
- **Expected**: 
  - Login returns 200 with session cookie/token
  - Protected endpoint returns 401 unauthenticated
  - Protected endpoint returns 200 authenticated
  
- **Evidence**:
  ```
  [Login response with Set-Cookie header]
  [401 response without auth]
  [200 response with auth]
  ```

## 4) Session Persistence (Restart & Duration)

- **Purpose**: Verify cookie/token survives browser restart; target ≥7 days persistence
- **Steps**:
  1. Open DevTools → Application → Cookies
  2. Note session cookie expiry date
  3. Close browser completely (Cmd+Q / Alt+F4)
  4. Reopen browser
  5. Navigate to app dashboard
  6. Confirm still logged in
  
- **Expected**: 
  - Session cookie expiry ≥7 days from creation
  - User remains authenticated after restart
  
- **Evidence**:
  ```
  [DevTools cookie screenshot showing expiry]
  [Dashboard access confirmed post-restart]
  ```

## 5) "Remember Me" Behavior

- **Purpose**: Verify extended session when checked
- **Steps**:
  1. Logout from current session
  2. Login WITHOUT "Remember me" checked
  3. Check cookie expiry in DevTools
  4. Logout again
  5. Login WITH "Remember me" checked
  6. Compare cookie expiry
  
- **Expected**: 
  - Without remember: Session or 24hr expiry
  - With remember: 7+ day expiry
  
- **Evidence**:
  ```
  [Cookie expiry without remember me]
  [Cookie expiry with remember me]
  ```

## 6) Password Reset

- **Purpose**: Confirm reset path and new credentials work
- **Steps**:
  1. Visit `/forgot-password`
  2. Enter `reset_user+auth2@example.com`
  3. Submit request
  4. Check email for reset link
  5. Click reset link
  6. Enter new password: `NewPass456!`
  7. Submit and confirm redirect
  8. Attempt login with old password (should fail)
  9. Login with new password (should succeed)
  
- **API Steps**:
  ```bash
  # Request reset
  curl -i -X POST https://coraai.tech/api/auth/forgot-password \
    -H "Content-Type: application/json" \
    -d '{"email":"reset_user+auth2@example.com"}'
  
  # Reset password (use token from email)
  curl -i -X POST https://coraai.tech/api/auth/reset-password \
    -H "Content-Type: application/json" \
    -d '{"token":"<TOKEN_FROM_EMAIL>","new_password":"NewPass456!"}'
  ```
  
- **Expected**: 
  - Reset email sent
  - Reset completes successfully
  - Old password rejected (401)
  - New password accepted (200)
  
- **Evidence**:
  ```
  [Reset email screenshot]
  [Reset success response]
  [Failed login with old password]
  [Successful login with new password]
  ```

## 7) Rate Limiting & Error Messaging

- **Purpose**: Ensure no crash and user-safe messages when abusing endpoints
- **Steps (API)**:
  ```bash
  # Rapid-fire login attempts with bad credentials
  for i in {1..20}; do
    curl -i -X POST https://coraai.tech/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{"email":"bad@example.com","password":"wrong"}' &
  done
  wait
  ```
  
- **Expected**: 
  - After N attempts (typically 5-10), receive 429 Too Many Requests
  - Error message is user-friendly
  - Service remains healthy (check /api/status)
  
- **Evidence**:
  ```
  [429 response with rate limit message]
  [/api/status still returns 200]
  ```

## 8) Preference Persistence (Timezone & Currency)

- **Purpose**: Confirm user settings persist through session
- **Steps**:
  1. Login as test user
  2. Navigate to profile/settings
  3. Change timezone to "Europe/London"
  4. Change currency to "EUR"
  5. Save settings
  6. Logout
  7. Login again
  8. Check profile settings
  9. Export a test CSV to verify timezone applied
  
- **API Verification**:
  ```bash
  # Get user profile
  curl -i https://coraai.tech/api/me -b cookies.txt
  
  # Update preferences
  curl -i -X PUT https://coraai.tech/api/profile \
    -H "Content-Type: application/json" \
    -b cookies.txt \
    -d '{"timezone":"Europe/London","currency":"EUR"}'
  ```
  
- **Expected**: 
  - Settings saved and persist across sessions
  - Exports use correct timezone
  - Currency displays correctly
  
- **Evidence**:
  ```
  [Settings before logout]
  [Settings after re-login]
  [Export filename showing timezone]
  ```

## 9) Smoke Re-check & Summary

- **Re-run**:
  ```bash
  # Health check
  curl -i https://coraai.tech/api/status
  
  # Protected route unauthenticated
  curl -i https://coraai.tech/api/dashboard
  
  # Protected route authenticated
  curl -i https://coraai.tech/api/dashboard -b cookies.txt
  ```
  
- **Expected**: 
  - /api/status → 200
  - Unauthenticated → 401
  - Authenticated → 200
  
- **Evidence**:
  ```
  [Final status check responses]
  ```

## Defects & Notes

| ID | Severity | Area | Steps to Reproduce | Expected | Actual | Evidence |
|----|----------|------|--------------------|---------|--------|----------|
| | | | | | | |
| | | | | | | |
| | | | | | | |

## Verdict

- **Pass/Fail**: [ ]
- **Follow-ups**:
  - Queue **Section 2 (Profile & Timezone)** walkthrough
  - Queue **Section 3 (Voice Entry & Expenses)** walkthrough
  - Document any UX copy issues for revision
  - Note any confusing flows for improvement
  
- **Artifacts**:
  - Evidence files saved under docs/ai-audits/2025-09-04/evidence/
  - Screenshots named: auth_[step]_[result].png
  - API responses saved as: auth_[endpoint]_response.txt