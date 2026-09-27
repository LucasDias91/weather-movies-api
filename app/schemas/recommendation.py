from pydantic import BaseModel, Field


class WeatherInfo(BaseModel):
    city: str
    country: str | None = None
    temperature_c: float
    description: str
    main: str
    icon: str | None = None


class MovieCard(BaseModel):
    tmdb_id: int
    title: str
    overview: str = ""
    poster_url: str | None = None
    genres: list[str] = Field(default_factory=list)
    vote_average: float = 0


class RecommendationResponse(BaseModel):
    weather: WeatherInfo
    mapped_genres: list[str]
    movies: list[MovieCard]


class PlaceSuggestion(BaseModel):
    name: str
    state: str | None = None
    country: str | None = None
    lat: float | None = None
    lon: float | None = None
