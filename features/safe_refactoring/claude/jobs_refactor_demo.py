#!/usr/bin/env python3
"""
DEMONSTRATION: How jobs.py would look with standardized errors
This is NOT the actual file - just showing the refactoring approach
"""

# At the top of jobs.py, we would add:
from features.safe_refactoring.claude.error_constants import (
    ErrorMessages,
    STATUS_NOT_FOUND,
    STATUS_BAD_REQUEST,
    ERROR_ALREADY_EXISTS
)

# Then replace all instances like this:

# OLD WAY (line 152):
# if not job:
#     raise HTTPException(status_code=404, detail="Job not found")

# NEW WAY:
if not job:
    raise HTTPException(
        status_code=STATUS_NOT_FOUND,
        detail=ErrorMessages.not_found("job")
    )

# OLD WAY (line 79):
# if existing_job:
#     raise HTTPException(status_code=400, detail="Job ID already exists")

# NEW WAY:
if existing_job:
    raise HTTPException(
        status_code=STATUS_BAD_REQUEST,
        detail=ErrorMessages.already_exists("job ID")
    )

# Benefits:
# 1. All 5 "Job not found" messages would be identical
# 2. Easy to change wording globally
# 3. Status codes are named constants (no magic numbers)
# 4. Ready for internationalization