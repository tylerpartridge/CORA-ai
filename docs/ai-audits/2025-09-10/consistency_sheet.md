# Export Date Range Consistency Sheet

This sheet standardizes parameter names and filename suffix rules across code, tests, and smokes.

## Params
- start: YYYY-MM-DD (inclusive)
- end: YYYY-MM-DD (inclusive)
- Inverted ranges auto-corrected so start <= end.

## Filenames
- None: `cora_{type}_{email}_{YYYYMMDD}.csv`
- Start only: `cora_{type}_{email}_{START}.csv`
- End only: `cora_{type}_{email}_{END}.csv`
- Both: `cora_{type}_{email}_{START-END}.csv`

## Endpoints
- `/api/expenses/export` → CSV
- `/api/dashboard/export?format=csv` → CSV

## Notes
- Behavior unchanged when no params.
- Tests and smoke scripts align to the rules above.