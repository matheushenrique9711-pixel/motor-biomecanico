#!/usr/bin/env python3
"""
Entry point para rodar a aplicação Motor Biomecânico.
Usage: python main.py
"""

import sys
from app.main import app

if __name__ == "__main__":
    import uvicorn

    # Roda o servidor
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
