from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_recommendation_service
from app.schemas.recommendation import RecommendationResponse
from app.services.errors import CityNotFoundError, ExternalApiError, MissingApiKeyError
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get(
    "",
    summary="Recomendar filmes pelo clima",
    description=(
        "Consulta a OpenWeatherMap (API externa), mapeia o clima para gêneros "
        "e devolve filmes do TMDB já tratados. Informe `city` ou `lat` e `lon`."
    ),
    response_model=RecommendationResponse,
)
def get_recommendations(
    city: str | None = Query(None, description="Nome da cidade, ex.: São Paulo"),
    lat: float | None = Query(None, description="Latitude"),
    lon: float | None = Query(None, description="Longitude"),
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationResponse:
    if not city and (lat is None or lon is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe city ou o par lat e lon",
        )

    try:
        return service.recommend(city=city, lat=lat, lon=lon)
    except MissingApiKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except CityNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ExternalApiError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
