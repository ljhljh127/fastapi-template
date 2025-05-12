"""
/app/api/v1/routers.py
"""

from fastapi import APIRouter

from app.api.v1.endpoints import example

api_router = APIRouter()

# if you want to add router add here
api_router.include_router(example.router, prefix="/example", tags=["example"])
