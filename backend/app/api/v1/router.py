from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.courses import router as courses_router
from app.api.v1.materials import router as materials_router
from app.api.v1.profile import router as profile_router
from app.api.v1.share import router as share_router
from app.api.v1.topics import router as topics_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(courses_router)
api_router.include_router(topics_router)
api_router.include_router(materials_router)
api_router.include_router(profile_router)
api_router.include_router(share_router)
