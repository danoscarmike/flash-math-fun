from datetime import datetime

from fastapi.responses import JSONResponse
from nicegui import app


@app.get("/health")
def health():
    """Health check endpoint for Cloud Run"""
    return JSONResponse(
        {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "flash-math-fun",
        }
    )
