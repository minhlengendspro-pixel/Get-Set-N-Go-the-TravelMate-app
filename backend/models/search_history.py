from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SearchHistorySchema(BaseModel):
    keyword: str = Field(..., min_length=1)
    destination: Optional[str] = None
    search_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)