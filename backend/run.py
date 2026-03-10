"""
Application Entry Point

This module serves as the main entry point for the SIMS (School Information Management System)
FastAPI backend application. It configures and starts the Uvicorn ASGI server with environment-based
settings for host, port, and hot-reload functionality.

Environment Variables:
    HOST (str): Server bind address (default: "0.0.0.0" for all interfaces)
    PORT (int): Server port number (default: 8000)
    RELOAD (str): Enable auto-reload on code changes (default: "false")

Usage:
    python run.py

Example:
    # Development mode with auto-reload
    RELOAD=true python run.py
    
    # Production mode on custom port
    PORT=8080 python run.py
"""

import uvicorn
import os
import sys

if __name__ == "__main__":
    # Get the directory containing this script (the 'backend' directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add it to sys.path so 'app' module can be found
    sys.path.insert(0, current_dir)
    
    # Run Uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)
