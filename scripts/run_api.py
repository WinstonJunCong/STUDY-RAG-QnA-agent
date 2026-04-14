#!/usr/bin/env python3
# run_api.py - Run the FastAPI server

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn


if __name__ == "__main__":
    print("Starting Studio Knowledge API...")
    print("Open http://localhost:8000/docs for API documentation")
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False  # Set to True for development
    )
