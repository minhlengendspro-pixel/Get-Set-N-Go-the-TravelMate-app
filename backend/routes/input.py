from fastapi import APIRouter, HTTPException
from backend.models.input_context import (
    InputContextRequest,
    InputContextResponse
)
from backend.services.tag_parser import extract_tags
from backend.services.input_score import calculate_tag_weights

router = APIRouter()

@router.post("/api/input/validate")
def validate_input(request: InputContextRequest):
    try:
        tags = extract_tags(
            request.interests,
            request.user_text
        )
        tag_weights = calculate_tag_weights(
            request.mode,
            tags
        )

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    response = InputContextResponse(
        destination=request.destination,
        mode=request.mode,
        tags=tags,
        tag_weights=tag_weights,
        budget=request.budget,
        duration=request.duration,
        allergies=request.allergies
    )
    return {
        "success": True,
        "message": "Input data is valid",
        "data": response.model_dump()
        }