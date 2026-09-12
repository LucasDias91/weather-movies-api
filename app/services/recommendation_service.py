from __future__ import annotations

from app.core.config import HEAT_THRESHOLD_C
from app.schemas.recommendation import RecommendationResponse
from app.services.movie_service import TMDB_GENRE_NAMES, MovieService
from app.services.weather_service import WeatherService

WEATHER_GENRE_IDS: dict[str, list[int]] = {
    "Thunderstorm": [27, 53, 18],
    "Drizzle": [27, 53, 18],
    "Rain": [27, 53, 18],
    "Snow": [10749, 10751],
    "Mist": [9648],
    "Smoke": [9648],
    "Haze": [9648],
    "Fog": [9648],
    "Sand": [9648],
    "Dust": [9648],
    "Ash": [27, 53],
    "Squall": [28, 53],
    "Tornado": [28, 53],
    "Clear": [35, 12],
    "Clouds": [99, 18],
}

DEFAULT_GENRE_IDS = [18, 35]


class RecommendationService:
    def __init__(self, weather_service: WeatherService, movie_service: MovieService) -> None:
        self._weather = weather_service
        self._movies = movie_service

    def recommend(
        self,
        *,
        city: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> RecommendationResponse:
        weather = self._weather.get_current(city=city, lat=lat, lon=lon)
        genre_ids = self._map_genres(weather.main, weather.temperature_c)
        movies = self._movies.discover_by_genre_ids(genre_ids)
        mapped_names = [TMDB_GENRE_NAMES[gid] for gid in genre_ids if gid in TMDB_GENRE_NAMES]
        return RecommendationResponse(
            weather=weather,
            mapped_genres=mapped_names,
            movies=movies,
        )

    @staticmethod
    def _map_genres(weather_main: str, temperature_c: float) -> list[int]:
        if temperature_c >= HEAT_THRESHOLD_C:
            return [28]
        return WEATHER_GENRE_IDS.get(weather_main, DEFAULT_GENRE_IDS)
