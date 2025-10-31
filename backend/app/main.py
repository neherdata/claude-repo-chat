"""
Claude Repo Chat - FastAPI Backend
Browser-based Claude interface for secure repository access
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)

logger = structlog.get_logger()

app = FastAPI(
    title="Claude Repo Chat",
    description="Browser-based Claude interface for secure repository access",
    version="0.1.0",
)

# CORS middleware (configure properly in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy", "service": "claude-repo-chat"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "service": "Claude Repo Chat",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )
