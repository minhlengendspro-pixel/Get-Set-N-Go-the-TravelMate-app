from fastapi import APIRouter
from backend.models.input_context import InputContextRequest
router = APIRouter()

@router.post("/api/input/validate")
def validate_input(request: InputContextRequest):
    return {
        "success": True,
        "message": "Input data is valid",
        "data": request.model_dump()
    }