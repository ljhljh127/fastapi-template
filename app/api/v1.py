from fastapi import APIRouter

from app.domains.example.router import router as example_router

api_router = APIRouter()
api_router.include_router(example_router)
