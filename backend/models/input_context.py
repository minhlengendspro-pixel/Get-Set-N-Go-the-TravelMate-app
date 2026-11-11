from pydantic import BaseModel, Field
from typing import Literal

class InputContextRequest(BaseModel):
    destination: str
    mode: Literal["solo","couple","family","random"]
    interests: list[str] = Field(default_factory=list)
    budget: int | None = Field(default=None, ge=0)
    duration: int = Field(..., ge=1, le=30)
    allergies: list[str] = Field(default_factory=list)
    user_text: str=""

class InputContextResponse(BaseModel):
    destination: str
    mode: Literal["solo","couple","family","random"]
    tags: list[str] = Field(default_factory=list)
    budget: int | None = Field(default=None, ge=0)
    duration: int = Field(..., ge=1, le=30)
    allergies: list[str] = Field(default_factory=list)

