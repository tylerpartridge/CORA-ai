# Delete Account — Gap Analysis (2025-09-09)

## Summary
Status: **PARTIAL IMPLEMENTATION**  
- Soft delete with 30-day grace period present.  
- Missing: dedicated tests, scheduled cleanup of expired deletions, explicit recovery mechanism.  
- Fragility: uses `setattr()` for schema-agnostic field setting.

## Evidence (from intel sweep)
- Router: `routes/account_management.py:58–86`
- Issues:
  - No tests for delete-account
  - No job for post-grace purge
  - Recovery path unspecified
  - `setattr()` usage fragile for schema changes

## Risks
- Data retention beyond intended window
- User trust/compliance impact
- Silent failures on schema drift

## Proposed Solution (future GREEN session)
1. Explicit domain fields (no `setattr`): `deleted_at`, `delete_requested_at`, `delete_token`
2. Grace window enforcement with scheduled purge job (systemd timer or Celery beat)
3. Recovery (undo) endpoint within grace window
4. End-to-end tests:
   - request deletion → mark + token
   - recover within window
   - purge after window
5. Audit trail events (request, recover, purge)

## Acceptance Criteria
- API:
  - `DELETE /api/account` → 202 with deletion scheduled
  - `POST /api/account/recover` within grace → 200; flags cleared
  - Purge job removes/archives records after N days
- Tests:
  - Unit + integration cover request/recover/purge paths
  - Edge cases: repeated requests, already-deleted, expired token
- Observability:
  - Log entries for request/recover/purge
  - Metrics counter for purged accounts
- Data:
  - No PII retained after purge (beyond legal archive policy if any)

## Next Steps
- Schedule GREEN session to implement per above
- Decide purge mechanism: systemd timer + python script vs. Celery beat
- Define legal retention policy (if applicable)

