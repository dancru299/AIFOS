from fastapi import APIRouter

from app.schemas import HealthResponse


router = APIRouter(tags=["system"])


@router.get("/healthz", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")

