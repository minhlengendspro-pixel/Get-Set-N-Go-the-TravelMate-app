from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional


class PlaceSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    destination: str
    description: Optional[str] = None
    category: str
    rating: float = 0.0
    image_url: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @field_validator("rating", mode="before")
    @classmethod
    def parse_rating(cls, v):
        if v is None or str(v).strip().lower() in ("", "not a number", "nan"):
            return 0.0

        if isinstance(v, (int, float)):
            return float(v)

        clean_str = str(v).split("/")[0].replace(",", ".").strip()

        try:
            return float(clean_str)
        except ValueError:
            return 0.0


class FoodSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    category: str
    price: int
    destination: str
    rating: float = 0.0
    description: Optional[str] = None
    image_url: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("rating", mode="before")
    @classmethod
    def parse_rating(cls, v):
        if v is None or str(v).strip().lower() in ("", "not a number", "nan"):
            return 0.0

        if isinstance(v, (int, float)):
            return float(v)

        clean_str = str(v).split("/")[0].replace(",", ".").strip()

        try:
            return float(clean_str)
        except ValueError:
            return 0.0