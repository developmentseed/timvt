"""timvt.endpoints.health: health check endpoints."""

from pydantic import BaseModel

from fastapi import APIRouter

router = APIRouter()


class Message(BaseModel):
    """Simple message."""

    message: str


@router.get("/healthz", response_model=Message)
async def ping():
    """Health check."""
    return Message(message="I wear a mask and I wash my hands!")
