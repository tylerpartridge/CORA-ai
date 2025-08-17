#!/usr/bin/env python3
"""
Simplest possible FastAPI server to test if anything works
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return HTMLResponse("<h1>CORA Test Server Works!</h1><p>If you see this, FastAPI is working.</p>")

@app.get("/test")
def test():
    return {"status": "ok", "message": "Test endpoint works"}

if __name__ == "__main__":
    print("Starting simple test server on http://localhost:8002")
    print("Try visiting: http://localhost:8002/")
    uvicorn.run(app, host="127.0.0.1", port=8002)