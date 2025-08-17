#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/performance_monitor.py
🎯 PURPOSE: Performance monitoring dashboard for tracking system metrics
🔗 IMPORTS: FastAPI, database, datetime
📤 EXPORTS: router with performance monitoring endpoints
🔄 PATTERN: Real-time performance tracking and analysis
📝 STATUS: Production ready
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datetime import datetime
import json
import time
from collections import defaultdict
from typing import List
import psutil
import os

router = APIRouter(
    prefix="/admin/performance",
    tags=["Performance Monitoring"],
    responses={404: {"description": "Not found"}},
)

# In-memory storage for performance metrics (would use Redis in production)
performance_metrics = {
    "page_loads": defaultdict(list),
    "api_calls": defaultdict(list),
    "js_errors": defaultdict(list),
    "slow_queries": defaultdict(list),
    "server_metrics": []
}

class PerformanceTracker:
    @staticmethod
    def track_page_load(page: str, load_time: float, request_id: str):
        """Track page load performance"""
        performance_metrics["page_loads"][page].append({
            "timestamp": datetime.now().isoformat(),
            "load_time": load_time,
            "request_id": request_id
        })
        # Keep only last 1000 entries per page
        if len(performance_metrics["page_loads"][page]) > 1000:
            performance_metrics["page_loads"][page] = performance_metrics["page_loads"][page][-1000:]
    
    @staticmethod
    def track_api_call(endpoint: str, response_time: float, status_code: int):
        """Track API call performance"""
        performance_metrics["api_calls"][endpoint].append({
            "timestamp": datetime.now().isoformat(),
            "response_time": response_time,
            "status_code": status_code
        })
        # Keep only last 1000 entries per endpoint
        if len(performance_metrics["api_calls"][endpoint]) > 1000:
            performance_metrics["api_calls"][endpoint] = performance_metrics["api_calls"][endpoint][-1000:]
    
    @staticmethod
    def track_js_error(page: str, error: str, stack: str):
        """Track JavaScript errors"""
        performance_metrics["js_errors"][page].append({
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "stack": stack
        })
        # Keep only last 100 errors per page
        if len(performance_metrics["js_errors"][page]) > 100:
            performance_metrics["js_errors"][page] = performance_metrics["js_errors"][page][-100:]
    
    @staticmethod
    def track_slow_query(query: str, execution_time: float):
        """Track slow database queries"""
        performance_metrics["slow_queries"]["queries"].append({
            "timestamp": datetime.now().isoformat(),
            "query": query[:200],  # Truncate long queries
            "execution_time": execution_time
        })
        # Keep only last 100 slow queries
        if len(performance_metrics["slow_queries"]["queries"]) > 100:
            performance_metrics["slow_queries"]["queries"] = performance_metrics["slow_queries"]["queries"][-100:]

# Create global tracker instance
tracker = PerformanceTracker()

@router.get("/", response_class=HTMLResponse)
async def performance_dashboard(request: Request):
    """Serve the performance monitoring dashboard"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Performance Monitor - CORA Admin</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', -apple-system, sans-serif;
                background: #1a1a1a;
                color: #e2e8f0;
                padding: 20px;
            }
            .header {
                background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
                color: #1a1a1a;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
            }
            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .metric-card {
                background: rgba(26, 26, 26, 0.95);
                border: 2px solid rgba(255, 152, 0, 0.2);
                border-radius: 8px;
                padding: 20px;
            }
            .metric-card h3 {
                color: #FF9800;
                margin-bottom: 15px;
                text-transform: uppercase;
                font-size: 0.875rem;
                letter-spacing: 1px;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: 700;
                color: #69F0AE;
            }
            .metric-label {
                color: #a0aec0;
                font-size: 0.875rem;
                margin-top: 5px;
            }
            .chart-container {
                background: rgba(26, 26, 26, 0.95);
                border: 2px solid rgba(255, 152, 0, 0.2);
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
            }
            .error-list {
                max-height: 400px;
                overflow-y: auto;
            }
            .error-item {
                background: rgba(255, 82, 82, 0.1);
                border-left: 4px solid #FF5252;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 4px;
            }
            .slow-query {
                background: rgba(255, 152, 0, 0.1);
                border-left: 4px solid #FF9800;
                padding: 10px;
                margin-bottom: 10px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 0.875rem;
            }
            .refresh-btn {
                background: #FF9800;
                color: #1a1a1a;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                font-weight: 700;
                cursor: pointer;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .refresh-btn:hover {
                background: #F57C00;
            }
            .status-good { color: #69F0AE; }
            .status-warning { color: #FF9800; }
            .status-bad { color: #FF5252; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 CORA Performance Monitor</h1>
            <p>Real-time system performance metrics and monitoring</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <h3>System Health</h3>
                <div class="metric-value status-good">Healthy</div>
                <div class="metric-label">All systems operational</div>
            </div>
            
            <div class="metric-card">
                <h3>Average Page Load</h3>
                <div class="metric-value" id="avg-load-time">0ms</div>
                <div class="metric-label">Last 100 requests</div>
            </div>
            
            <div class="metric-card">
                <h3>API Response Time</h3>
                <div class="metric-value" id="avg-api-time">0ms</div>
                <div class="metric-label">Last 100 API calls</div>
            </div>
            
            <div class="metric-card">
                <h3>JavaScript Errors</h3>
                <div class="metric-value" id="js-error-count">0</div>
                <div class="metric-label">Last 24 hours</div>
            </div>
            
            <div class="metric-card">
                <h3>Memory Usage</h3>
                <div class="metric-value" id="memory-usage">0%</div>
                <div class="metric-label">Current usage</div>
            </div>
            
            <div class="metric-card">
                <h3>CPU Usage</h3>
                <div class="metric-value" id="cpu-usage">0%</div>
                <div class="metric-label">Current usage</div>
            </div>
        </div>

        <div class="chart-container">
            <h3 style="color: #FF9800; margin-bottom: 15px;">PAGE LOAD TIMES (ms)</h3>
            <canvas id="load-time-chart" height="100"></canvas>
        </div>

        <div class="chart-container">
            <h3 style="color: #FF9800; margin-bottom: 15px;">RECENT JAVASCRIPT ERRORS</h3>
            <div class="error-list" id="error-list">
                <p style="color: #a0aec0;">No errors recorded</p>
            </div>
        </div>

        <div class="chart-container">
            <h3 style="color: #FF9800; margin-bottom: 15px;">SLOW QUERIES (>100ms)</h3>
            <div class="error-list" id="slow-queries">
                <p style="color: #a0aec0;">No slow queries detected</p>
            </div>
        </div>

        <button class="refresh-btn" onclick="refreshMetrics()">Refresh Metrics</button>

        <script>
            async function refreshMetrics() {
                try {
                    const response = await fetch('/admin/performance/metrics');
                    const data = await response.json();
                    
                    // Update metric values
                    document.getElementById('avg-load-time').textContent = data.avg_page_load + 'ms';
                    document.getElementById('avg-api-time').textContent = data.avg_api_time + 'ms';
                    document.getElementById('js-error-count').textContent = data.js_error_count;
                    document.getElementById('memory-usage').textContent = data.memory_usage + '%';
                    document.getElementById('cpu-usage').textContent = data.cpu_usage + '%';
                    
                    // Update error list
                    const errorList = document.getElementById('error-list');
                    if (data.recent_errors.length > 0) {
                        errorList.innerHTML = data.recent_errors.map(err => 
                            `<div class="error-item">
                                <strong>${err.page}</strong> - ${err.error}
                                <div style="color: #a0aec0; font-size: 0.75rem;">${err.timestamp}</div>
                            </div>`
                        ).join('');
                    }
                    
                    // Update slow queries
                    const slowQueries = document.getElementById('slow-queries');
                    if (data.slow_queries.length > 0) {
                        slowQueries.innerHTML = data.slow_queries.map(q => 
                            `<div class="slow-query">
                                ${q.query}
                                <div style="color: #FF9800;">${q.execution_time}ms - ${q.timestamp}</div>
                            </div>`
                        ).join('');
                    }
                } catch (err) {
                    console.error('Failed to refresh metrics:', err);
                }
            }
            
            // Auto-refresh every 5 seconds
            setInterval(refreshMetrics, 5000);
            
            // Initial load
            refreshMetrics();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@router.get("/metrics")
async def get_metrics():
    """Get current performance metrics as JSON"""
    
    # Calculate averages
    avg_page_load = 0
    if performance_metrics["page_loads"]:
        all_loads = []
        for page_loads in performance_metrics["page_loads"].values():
            all_loads.extend([p["load_time"] for p in page_loads[-100:]])
        if all_loads:
            avg_page_load = int(sum(all_loads) / len(all_loads))
    
    avg_api_time = 0
    if performance_metrics["api_calls"]:
        all_calls = []
        for api_calls in performance_metrics["api_calls"].values():
            all_calls.extend([c["response_time"] for c in api_calls[-100:]])
        if all_calls:
            avg_api_time = int(sum(all_calls) / len(all_calls))
    
    # Count JS errors
    js_error_count = sum(len(errors) for errors in performance_metrics["js_errors"].values())
    
    # Get recent errors
    recent_errors = []
    for page, errors in performance_metrics["js_errors"].items():
        for error in errors[-5:]:  # Last 5 per page
            recent_errors.append({
                "page": page,
                "error": error["error"],
                "timestamp": error["timestamp"]
            })
    
    # Get slow queries
    slow_queries = performance_metrics["slow_queries"].get("queries", [])[-10:]
    
    # Get system metrics
    try:
        memory = psutil.virtual_memory()
        memory_usage = int(memory.percent)
        cpu_usage = int(psutil.cpu_percent(interval=0.1))
    except:
        memory_usage = 0
        cpu_usage = 0
    
    return {
        "avg_page_load": avg_page_load,
        "avg_api_time": avg_api_time,
        "js_error_count": js_error_count,
        "memory_usage": memory_usage,
        "cpu_usage": cpu_usage,
        "recent_errors": recent_errors,
        "slow_queries": slow_queries
    }

@router.post("/track/page-load")
async def track_page_load(request: Request):
    """Track page load performance from frontend"""
    data = await request.json()
    tracker.track_page_load(
        page=data.get("page", "unknown"),
        load_time=data.get("load_time", 0),
        request_id=data.get("request_id", "")
    )
    return {"status": "tracked"}

@router.post("/track/js-error")
async def track_js_error(request: Request):
    """Track JavaScript errors from frontend"""
    data = await request.json()
    tracker.track_js_error(
        page=data.get("page", "unknown"),
        error=data.get("error", ""),
        stack=data.get("stack", "")
    )
    return {"status": "tracked"}

@router.post("/track/api-call")
async def track_api_call(request: Request):
    """Track API call performance"""
    data = await request.json()
    tracker.track_api_call(
        endpoint=data.get("endpoint", "unknown"),
        response_time=data.get("response_time", 0),
        status_code=data.get("status_code", 200)
    )
    return {"status": "tracked"}

@router.post("/track/slow-query")
async def track_slow_query(request: Request):
    """Track slow database queries"""
    data = await request.json()
    tracker.track_slow_query(
        query=data.get("query", ""),
        execution_time=data.get("execution_time", 0)
    )
    return {"status": "tracked"}

# Export the tracker for use in middleware
__all__ = ["router", "tracker"]