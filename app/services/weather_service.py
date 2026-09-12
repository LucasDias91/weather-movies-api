from __future__ import annotations

import httpx

from app.core.config import (
    HTTP_TIMEOUT_SECONDS,
    OPENWEATHER_API_KEY,
    OPENWEATHER_BASE_URL,
)
from app.schemas.recommendation import WeatherInfo
from app.services.errors import CityNotFoundError, ExternalApiError, MissingApiKeyError


class WeatherService:
    def get_current(
        self,
        *,
        city: str | None = None,
        lat: float | None = None,
        lon: float | None = None,
    ) -> WeatherInfo:
        if not OPENWEATHER_API_KEY:
            raise MissingApiKeyError("OpenWeatherMap")

        params: dict[str, str | float] = {
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "pt_br",
        }
        if city:
            params["q"] = city
        else:
            params["lat"] = lat if lat is not None else 0
            params["lon"] = lon if lon is not None else 0

        url = f"{OPENWEATHER_BASE_URL}/data/2.5/weather"
        try:
            response = httpx.get(url, params=params, timeout=HTTP_TIMEOUT_SECONDS)
        except httpx.HTTPError as exc:
            raise ExternalApiError("OpenWeatherMap", str(exc)) from exc

        if response.status_code == 404:
            raise CityNotFoundError(city or f"{lat},{lon}")
        if response.status_code == 401:
            raise ExternalApiError("OpenWeatherMap", "API key inválida")
        if response.status_code >= 400:
            raise ExternalApiError("OpenWeatherMap", response.text[:300])

        payload = response.json()
        weather_list = payload.get("weather") or [{}]
        first = weather_list[0]
        main_block = payload.get("main") or {}
        sys_block = payload.get("sys") or {}

        return WeatherInfo(
            city=payload.get("name") or city or "",
            country=sys_block.get("country"),
            temperature_c=float(main_block.get("temp") or 0),
            description=first.get("description") or "",
            main=first.get("main") or "",
            icon=first.get("icon"),
        )
