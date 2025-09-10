#!/usr/bin/env python3
"""
LOCATION: tools/seed_job_types.py
PURPOSE: Seed canonical job types (idempotent)
USAGE: python tools/seed_job_types.py
"""

from models import SessionLocal  # type: ignore
from models import JobType  # type: ignore

CANON = [
    "General Contractor",
    "Plumbing",
    "Electrical",
    "HVAC",
    "Remodeling",
    "Roofing",
    "Concrete",
    "Painting",
    "Framing",
]


def main():
    db = SessionLocal()
    try:
        for name in CANON:
            exists = db.query(JobType).filter(JobType.name == name, JobType.user_id == None).first()  # noqa: E711
            if not exists:
                db.add(JobType(name=name, user_id=None))
        db.commit()
        print({"seeded": True, "count": len(CANON)})
    finally:
        db.close()


if __name__ == "__main__":
    main()

