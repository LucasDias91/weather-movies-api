from datetime import UTC, datetime

from app.models.watchlist_item import WatchlistItem
from app.repositories.watchlist_repository import WatchlistRepository
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate
from app.services.errors import DuplicateWatchlistError, WatchlistItemNotFoundError


class WatchlistService:
    def __init__(self, repository: WatchlistRepository) -> None:
        self._items = repository

    def create(self, data: WatchlistCreate) -> WatchlistItem:
        existing = self._items.get_by_tmdb_id(data.tmdb_id)
        if existing is not None:
            raise DuplicateWatchlistError(data.tmdb_id)

        entity = WatchlistItem(
            tmdb_id=data.tmdb_id,
            title=data.title,
            poster_url=data.poster_url,
            genre=data.genre,
            status=data.status,
            rating=data.rating,
            weather_label=data.weather_label,
            city=data.city,
            created_at=datetime.now(UTC).replace(tzinfo=None),
        )
        return self._items.create(entity)

    def get(self, item_id: int) -> WatchlistItem:
        item = self._items.get_by_id(item_id)
        if item is None:
            raise WatchlistItemNotFoundError(item_id)
        return item

    def list_page(
        self,
        *,
        status: str | None,
        sort: str,
        page: int,
        page_size: int,
    ) -> tuple[list[WatchlistItem], int]:
        return self._items.list_page(
            status=status,
            sort=sort,
            page=page,
            page_size=page_size,
        )

    def update(self, item_id: int, data: WatchlistUpdate) -> WatchlistItem:
        item = self.get(item_id)
        if data.status is not None:
            item.status = data.status
        if data.rating is not None:
            item.rating = data.rating
        return self._items.update(item)

    def delete(self, item_id: int) -> None:
        item = self.get(item_id)
        self._items.delete(item)
