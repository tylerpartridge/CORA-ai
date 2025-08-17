#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/routes/websocket.py
🎯 PURPOSE: WebSocket endpoints for real-time updates
🔗 IMPORTS: FastAPI WebSocket, dependencies
📤 EXPORTS: WebSocket routes and connection manager
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, Optional
import json
from datetime import datetime

from services.auth_service import verify_token

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store connection metadata
        self.connection_info: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        # Add to user's connection set
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Store connection metadata
        self.connection_info[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow().isoformat()
        }
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "message": "Connected to CORA real-time updates"
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        # Get user_id from connection info
        if websocket in self.connection_info:
            user_id = self.connection_info[websocket]["user_id"]
            
            # Remove from user's connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                
                # Clean up empty sets
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove connection info
            del self.connection_info[websocket]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message to WebSocket: {e}")
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """Send a message to all connections for a specific user"""
        if user_id in self.active_connections:
            # Send to all user's connections
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Mark for removal if send fails
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected clients"""
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass  # Ignore failed sends in broadcast

# Create global connection manager
manager = ConnectionManager()

async def get_user_from_token(token: str) -> Optional[str]:
    """Extract user email from JWT token"""
    try:
        email = verify_token(token)
        return email
    except Exception:
        return None

# WebSocket endpoint
async def websocket_endpoint(websocket: WebSocket, app):
    """Main WebSocket endpoint for real-time updates"""
    # Get token from query parameters
    token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=4001, reason="No authentication token provided")
        return
    
    # Verify token and get user
    user_email = await get_user_from_token(token)
    if not user_email:
        await websocket.close(code=4002, reason="Invalid authentication token")
        return
    
    # Connect the WebSocket
    await manager.connect(websocket, user_email)
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for incoming messages
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "ping":
                # Respond to ping with pong
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, websocket)
            
            elif data.get("type") == "subscribe":
                # Handle subscription requests (for future use)
                channel = data.get("channel")
                await manager.send_personal_message({
                    "type": "subscribed",
                    "channel": channel,
                    "status": "success"
                }, websocket)
            
            else:
                # Echo unknown messages back (for debugging)
                await manager.send_personal_message({
                    "type": "echo",
                    "original": data
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
        await websocket.close(code=4003, reason="Internal server error")

# Helper functions for broadcasting updates
async def broadcast_expense_update(user_id: str, expense_data: dict):
    """Broadcast expense creation/update to user"""
    await manager.broadcast_to_user(user_id, {
        "type": "expense_update",
        "data": expense_data,
        "timestamp": datetime.utcnow().isoformat()
    })

async def broadcast_job_update(user_id: str, job_data: dict):
    """Broadcast job update to user"""
    await manager.broadcast_to_user(user_id, {
        "type": "job_update",
        "data": job_data,
        "timestamp": datetime.utcnow().isoformat()
    })

async def broadcast_alert(user_id: str, alert_data: dict):
    """Broadcast new alert to user"""
    await manager.broadcast_to_user(user_id, {
        "type": "alert",
        "data": alert_data,
        "timestamp": datetime.utcnow().isoformat()
    })

# Export for use in other modules
__all__ = ['manager', 'broadcast_expense_update', 'broadcast_job_update', 'broadcast_alert']