from fastapi import APIRouter

from app.api.models import HealthResponse

router = APIRouter(prefix="/health", tags=["services"])


@router.get("/", response_model=HealthResponse)
async def app_health():
    return HealthResponse(status="ok")
