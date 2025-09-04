#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/core/app_endpoints.py
🎯 PURPOSE: Aggregates registration of core endpoints split into submodules
🔗 IMPORTS: Submodule registrars
📤 EXPORTS: register_core_endpoints(app, server_start_time)
"""

from datetime import datetime
from fastapi import FastAPI


def register_core_endpoints(app: FastAPI, server_start_time: datetime) -> None:
    from .app_endpoints_public import register_public_endpoints
    from .app_endpoints_misc import register_misc_endpoints

    register_public_endpoints(app, server_start_time)
    register_misc_endpoints(app)


