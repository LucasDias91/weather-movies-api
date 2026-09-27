from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.api.deps import get_weather_service
from app.services.errors import ExternalApiError, InvalidWeatherIconError
from app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["recommendations"])


@router.get(
    "/icons/{icon}",
    summary="Ícone do clima",
    description=(
        "Devolve o PNG do ícone OpenWeather. O navegador fala só com esta API; "
        "ela busca a imagem e a repassa."
    ),
    responses={200: {"content": {"image/png": {}}}},
)
def get_weather_icon(
    icon: str,
    service: WeatherService = Depends(get_weather_service),
) -> Response:
    try:
        content, media_type = service.fetch_icon(icon)
    except InvalidWeatherIconError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except ExternalApiError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return Response(
        content=content,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )
