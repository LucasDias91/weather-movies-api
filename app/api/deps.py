from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.watchlist_repository import WatchlistRepository
from app.services.movie_service import MovieService
from app.services.recommendation_service import RecommendationService
from app.services.watchlist_service import WatchlistService
from app.services.weather_service import WeatherService


def get_watchlist_service(db: Session = Depends(get_db)) -> WatchlistService:
    return WatchlistService(WatchlistRepository(db))


def get_recommendation_service() -> RecommendationService:
    return RecommendationService(WeatherService(), MovieService())
