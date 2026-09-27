import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# Chaves da entrega. Um .env local substitui estes valores.
_OPENWEATHER_KEY = "10112d0b2aafe22c63cf823ae0203080"
_TMDB_KEY = "be9580ddba8f4ca443282cd72f937c6c"

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "").strip() or _OPENWEATHER_KEY
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "").strip() or _TMDB_KEY
OPENWEATHER_BASE_URL = os.environ.get(
    "OPENWEATHER_BASE_URL", "https://api.openweathermap.org"
).rstrip("/")
OPENWEATHER_ICON_BASE_URL = os.environ.get(
    "OPENWEATHER_ICON_BASE_URL", "https://openweathermap.org/img/wn"
).rstrip("/")
TMDB_BASE_URL = os.environ.get("TMDB_BASE_URL", "https://api.themoviedb.org/3").rstrip("/")
TMDB_IMAGE_BASE_URL = os.environ.get(
    "TMDB_IMAGE_BASE_URL", "https://image.tmdb.org/t/p/w500"
).rstrip("/")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./weather_movies.db")
HTTP_TIMEOUT_SECONDS = float(os.environ.get("HTTP_TIMEOUT_SECONDS", "10"))
HEAT_THRESHOLD_C = float(os.environ.get("HEAT_THRESHOLD_C", "32"))
