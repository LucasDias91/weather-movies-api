from __future__ import annotations

import re
import unicodedata

import httpx

from app.core.config import (
    HTTP_TIMEOUT_SECONDS,
    OPENWEATHER_API_KEY,
    OPENWEATHER_BASE_URL,
    OPENWEATHER_ICON_BASE_URL,
)
from app.schemas.recommendation import PlaceSuggestion, WeatherInfo
from app.services.errors import (
    CityNotFoundError,
    ExternalApiError,
    InvalidWeatherIconError,
    MissingApiKeyError,
)

_ICON_CODE = re.compile(r"^(01|02|03|04|09|10|11|13|50)[dn]$")


_MUNICIPALITIES: list[tuple[str, str]] | None = None
_IBGE_MUNICIPIOS_URL = (
    "https://servicodados.ibge.gov.br/api/v1/localidades/municipios?orderBy=nome"
)


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(char for char in normalized if unicodedata.category(char) != "Mn").casefold()


def _state_code(item: dict) -> str | None:
    micro = (item.get("microrregiao") or {}).get("mesorregiao") or {}
    uf = (micro.get("UF") or {}).get("sigla")
    if uf:
        return uf
    immediate = (item.get("regiao-imediata") or {}).get("regiao-intermediaria") or {}
    return (immediate.get("UF") or {}).get("sigla")


def _brazilian_municipalities() -> list[tuple[str, str]]:
    global _MUNICIPALITIES
    if _MUNICIPALITIES is not None:
        return _MUNICIPALITIES

    response = httpx.get(_IBGE_MUNICIPIOS_URL, timeout=max(HTTP_TIMEOUT_SECONDS, 20))
    response.raise_for_status()
    rows: list[tuple[str, str]] = []
    for item in response.json() or []:
        name = (item.get("nome") or "").strip()
        state = _state_code(item)
        if name and state:
            rows.append((name, state))
    _MUNICIPALITIES = rows
    return rows


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

    def search_places(self, query: str, *, limit: int = 6) -> list[PlaceSuggestion]:
        folded = _fold(query.strip())
        if len(folded) < 2:
            return []

        try:
            matches = [
                PlaceSuggestion(name=name, state=state, country="BR")
                for name, state in _brazilian_municipalities()
                if _fold(name).startswith(folded)
            ]
        except httpx.HTTPError:
            matches = []

        if matches:
            return matches[:limit]

        return self._search_openweather_places(query.strip(), folded, limit=limit)

    def _search_openweather_places(
        self,
        query: str,
        folded: str,
        *,
        limit: int,
    ) -> list[PlaceSuggestion]:
        if not OPENWEATHER_API_KEY:
            raise MissingApiKeyError("OpenWeatherMap")

        url = f"{OPENWEATHER_BASE_URL}/geo/1.0/direct"
        params = {"q": query, "limit": 10, "appid": OPENWEATHER_API_KEY}
        try:
            response = httpx.get(url, params=params, timeout=HTTP_TIMEOUT_SECONDS)
        except httpx.HTTPError as exc:
            raise ExternalApiError("OpenWeatherMap", str(exc)) from exc

        if response.status_code == 401:
            raise ExternalApiError("OpenWeatherMap", "API key inválida")
        if response.status_code >= 400:
            raise ExternalApiError("OpenWeatherMap", response.text[:300])

        places: list[PlaceSuggestion] = []
        for item in response.json() or []:
            local_names = item.get("local_names") or {}
            name = local_names.get("pt") or item.get("name") or ""
            if not name or not _fold(name).startswith(folded):
                continue
            places.append(
                PlaceSuggestion(
                    name=name,
                    state=item.get("state"),
                    country=item.get("country"),
                    lat=float(item["lat"]) if item.get("lat") is not None else None,
                    lon=float(item["lon"]) if item.get("lon") is not None else None,
                )
            )
        brazilian = [place for place in places if (place.country or "").upper() == "BR"]
        return (brazilian or places)[:limit]

    def fetch_icon(self, icon: str) -> tuple[bytes, str]:
        if not _ICON_CODE.fullmatch(icon):
            raise InvalidWeatherIconError(icon)

        url = f"{OPENWEATHER_ICON_BASE_URL}/{icon}@2x.png"
        try:
            response = httpx.get(url, timeout=HTTP_TIMEOUT_SECONDS)
        except httpx.HTTPError as exc:
            raise ExternalApiError("OpenWeatherMap", str(exc)) from exc

        if response.status_code >= 400:
            raise ExternalApiError("OpenWeatherMap", f"ícone {icon} indisponível")

        media_type = response.headers.get("content-type", "image/png").split(";", 1)[0].strip()
        if not media_type.startswith("image/"):
            media_type = "image/png"
        return response.content, media_type
