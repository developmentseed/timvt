"""TiVTiler.endpoints.health: health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class Message(BaseModel):
    message: str


@router.get("/healthz", response_model=Message)
async def ping():
    """Health check."""
    return Message(message="I wear a mask and I wash my hands!")
