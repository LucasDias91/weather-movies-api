from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_weather_service
from app.schemas.recommendation import PlaceSuggestion
from app.services.errors import ExternalApiError, MissingApiKeyError
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/locations", tags=["recommendations"])


@router.get(
    "",
    summary="Sugerir cidades",
    description="Autocomplete de localização via geocoding da OpenWeatherMap.",
    response_model=list[PlaceSuggestion],
)
def search_locations(
    q: str = Query(..., min_length=2, description="Trecho do nome da cidade"),
    service: WeatherService = Depends(get_weather_service),
) -> list[PlaceSuggestion]:
    try:
        return service.search_places(q)
    except MissingApiKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except ExternalApiError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
