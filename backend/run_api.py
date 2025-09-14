#!/usr/bin/env python
"""
Run the FastAPI server directly
"""

import uvicorn
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

if __name__ == "__main__":
    print("🚀 Starting FinanceGPT Pro API Server...")
    print("📚 API Documentation will be available at: http://localhost:8000/docs")
    print("🌐 API Base URL: http://localhost:8000")
    print("-" * 50)

    # Run the FastAPI app
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )