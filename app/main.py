"""
FastAPI Template main
"""

from fastapi import FastAPI

from app.api.v1.routers import api_router
from app.core.config import conf

app = FastAPI(
    title="FastAPI Template",
    description="API documentation",
    version="1.0.0",
)

config = conf

print(f"INFO | was server starting on {conf.app_env} env...")

app.include_router(api_router, prefix="/api/v1")
