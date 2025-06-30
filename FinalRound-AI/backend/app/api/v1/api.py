from fastapi import APIRouter

from .endpoints import interview, resume, users

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(interview.router, prefix="/interview", tags=["interview"])
api_router.include_router(resume.router, prefix="/resume", tags=["resume"])
