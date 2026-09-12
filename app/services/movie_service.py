from __future__ import annotations

import httpx

from app.core.config import (
    HTTP_TIMEOUT_SECONDS,
    TMDB_API_KEY,
    TMDB_BASE_URL,
    TMDB_IMAGE_BASE_URL,
)
from app.schemas.recommendation import MovieCard
from app.services.errors import ExternalApiError, MissingApiKeyError

TMDB_GENRE_NAMES = {
    12: "Aventura",
    18: "Drama",
    27: "Terror",
    28: "Ação",
    35: "Comédia",
    53: "Thriller",
    99: "Documentário",
    9648: "Mistério",
    10749: "Romance",
    10751: "Família",
}


class MovieService:
    def discover_by_genre_ids(self, genre_ids: list[int], *, limit: int = 12) -> list[MovieCard]:
        if not TMDB_API_KEY:
            raise MissingApiKeyError("TMDB")

        url = f"{TMDB_BASE_URL}/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": ",".join(str(gid) for gid in genre_ids),
            "language": "pt-BR",
            "sort_by": "popularity.desc",
            "include_adult": "false",
        }
        try:
            response = httpx.get(url, params=params, timeout=HTTP_TIMEOUT_SECONDS)
        except httpx.HTTPError as exc:
            raise ExternalApiError("TMDB", str(exc)) from exc

        if response.status_code == 401:
            raise ExternalApiError("TMDB", "API key inválida")
        if response.status_code >= 400:
            raise ExternalApiError("TMDB", response.text[:300])

        results = (response.json().get("results") or [])[:limit]
        movies: list[MovieCard] = []
        for item in results:
            poster_path = item.get("poster_path")
            movies.append(
                MovieCard(
                    tmdb_id=int(item.get("id") or 0),
                    title=item.get("title") or item.get("original_title") or "",
                    overview=item.get("overview") or "",
                    poster_url=f"{TMDB_IMAGE_BASE_URL}{poster_path}" if poster_path else None,
                    genres=[
                        TMDB_GENRE_NAMES[gid]
                        for gid in (item.get("genre_ids") or [])
                        if gid in TMDB_GENRE_NAMES
                    ],
                    vote_average=float(item.get("vote_average") or 0),
                )
            )
        return movies
