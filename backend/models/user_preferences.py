from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field

class UserPreferences(BaseModel):
    destination: str
    mode: Literal["solo", "couple", "family", "random"]
    interests: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    budget: int | None = Field(default=None, ge=0)
    duration: int = Field(..., ge=1, le=30)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
