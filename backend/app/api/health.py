from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Simple liveness check for the backend API."""
    return {
        "status": "ok",
        "app": "Eternal Mind",
        "version": "1.0"
    }