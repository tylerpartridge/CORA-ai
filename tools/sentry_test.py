#!/usr/bin/env python3
"""
Send a synthetic Sentry exception if SENTRY_DSN is set.
Prints a single confirmation line and exits 0.
"""

import os
import sys


def main() -> int:
    dsn = os.getenv("SENTRY_DSN") or os.getenv("CORA_SENTRY_DSN")
    if not dsn:
        print("Sentry DSN not set; skipping")
        return 0

    try:
        import sentry_sdk  # already in requirements
        sentry_sdk.init(dsn=dsn, traces_sample_rate=0.0)
        sentry_sdk.capture_exception(ZeroDivisionError("synthetic test event"))
        try:
            sentry_sdk.flush(2.0)
        except Exception:
            pass
        print("Sentry test event sent.")
    except Exception as e:
        # Still exit 0 to avoid scheduler noise
        print(f"Sentry test failed softly: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

