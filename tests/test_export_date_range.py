#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tests/test_export_date_range.py
🎯 PURPOSE: Validate export filename generation with optional date ranges
🔗 IMPORTS: pytest, utils.filenames
📤 EXPORTS: Test cases for range suffix behavior
"""

import re
import pytest
from datetime import datetime, timezone

from utils.filenames import generate_filename


def _parts(filename: str):
    # cora_{type}_{email}_{suffix}.csv
    assert filename.startswith("cora_") and filename.endswith(".csv")
    core = filename[len("cora_"):-4]
    return core.split("_")


class TestExportFilenameDateRange:
    def test_no_params_uses_today(self):
        fn = generate_filename("expenses", "user@example.com", "UTC", when=datetime(2025, 9, 10, tzinfo=timezone.utc))
        assert fn == "cora_expenses_user_at_example.com_20250910.csv"

    def test_start_only(self):
        fn = generate_filename("expenses", "user@example.com", "UTC", when=datetime(2025, 9, 10, tzinfo=timezone.utc), date_start="2025-09-01")
        # Expect compact start-only suffix (per current implementation: single compacted date)
        assert fn == "cora_expenses_user_at_example.com_20250901.csv"

    def test_end_only(self):
        fn = generate_filename("expenses", "user@example.com", "UTC", when=datetime(2025, 9, 10, tzinfo=timezone.utc), date_end="2025-09-30")
        assert fn == "cora_expenses_user_at_example.com_20250930.csv"

    def test_both_start_end(self):
        fn = generate_filename("expenses", "user@example.com", "UTC", when=datetime(2025, 9, 10, tzinfo=timezone.utc), date_start="2025-09-01", date_end="2025-09-30")
        assert fn == "cora_expenses_user_at_example.com_20250901-20250930.csv"

    def test_inverted_auto_corrects(self):
        fn = generate_filename("expenses", "user@example.com", "UTC", when=datetime(2025, 9, 10, tzinfo=timezone.utc), date_start="2025-09-30", date_end="2025-09-01")
        # auto-corrected order
        assert fn == "cora_expenses_user_at_example.com_20250901-20250930.csv"


