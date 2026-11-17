from pydantic import BaseModel, Field, field_validator
from typing import Literal

class InputContextRequest(BaseModel):
    destination: str
    mode: Literal["solo","couple","family","random"]
    interests: list[str] = Field(default_factory=list)
    budget: int | None = Field(default=None, ge=0)
    duration: int = Field(..., ge=1, le=30)
    allergies: list[str] = Field(default_factory=list)
    user_text: str=""

    @field_validator("user_text")
    def validate_user_text(value: str):
        word_count = len(value.split())
        if word_count > 30:
            raise ValueError("user_text không được vượt quá 30 từ")
        return value

class InputContextResponse(BaseModel):
    destination: str
    mode: Literal["solo","couple","family","random"]
    tags: list[str] = Field(default_factory=list)
    budget: int | None = Field(default=None, ge=0)
    duration: int = Field(..., ge=1, le=30)
    allergies: list[str] = Field(default_factory=list)

