class MissingApiKeyError(Exception):
    def __init__(self, provider: str) -> None:
        self.provider = provider
        super().__init__(f"Missing API key for {provider}")


class CityNotFoundError(Exception):
    def __init__(self, city: str) -> None:
        self.city = city
        super().__init__(f"City not found: {city}")


class ExternalApiError(Exception):
    def __init__(self, provider: str, detail: str) -> None:
        self.provider = provider
        self.detail = detail
        super().__init__(f"{provider}: {detail}")


class WatchlistItemNotFoundError(Exception):
    def __init__(self, item_id: int) -> None:
        self.item_id = item_id
        super().__init__(f"Watchlist item id={item_id} not found")


class DuplicateWatchlistError(Exception):
    def __init__(self, tmdb_id: int) -> None:
        self.tmdb_id = tmdb_id
        super().__init__(f"Movie tmdb_id={tmdb_id} is already in the watchlist")
