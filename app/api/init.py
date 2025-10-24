from fastapi import APIRouter

from app.api.chat import router as chat_router
from app.api.services import router as services_router
from app.api.files import router as files_router
from config import Config

api_router = APIRouter(prefix=Config.api_prefix)
api_router.include_router(chat_router, tags=["chat"])
api_router.include_router(services_router, tags=["services"])
api_router.include_router(files_router, tags=["files"])
