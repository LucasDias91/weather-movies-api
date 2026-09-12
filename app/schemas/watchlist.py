from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

WatchlistStatus = Literal["quero_assistir", "assistido"]


class WatchlistCreate(BaseModel):
    tmdb_id: int = Field(..., ge=1)
    title: str = Field(..., min_length=1, max_length=255)
    poster_url: str | None = Field(None, max_length=500)
    genre: str | None = Field(None, max_length=255)
    weather_label: str | None = Field(None, max_length=120)
    city: str | None = Field(None, max_length=120)
    status: WatchlistStatus = "quero_assistir"
    rating: float | None = Field(None, ge=0, le=10)


class WatchlistUpdate(BaseModel):
    status: WatchlistStatus | None = None
    rating: float | None = Field(None, ge=0, le=10)


class WatchlistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tmdb_id: int
    title: str
    poster_url: str | None
    genre: str | None
    status: str
    rating: float | None
    weather_label: str | None
    city: str | None
    created_at: datetime


class WatchlistPage(BaseModel):
    items: list[WatchlistResponse]
    total: int
    page: int
    page_size: int
