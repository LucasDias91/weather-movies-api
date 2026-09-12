from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.watchlist_item import WatchlistItem

_SORT_COLUMNS = {
    "created_at": WatchlistItem.created_at,
    "title": WatchlistItem.title,
    "rating": WatchlistItem.rating,
    "id": WatchlistItem.id,
}


class WatchlistRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, item: WatchlistItem) -> WatchlistItem:
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def get_by_id(self, item_id: int) -> WatchlistItem | None:
        return self._db.get(WatchlistItem, item_id)

    def get_by_tmdb_id(self, tmdb_id: int) -> WatchlistItem | None:
        stmt = select(WatchlistItem).where(WatchlistItem.tmdb_id == tmdb_id)
        return self._db.scalar(stmt)

    def update(self, item: WatchlistItem) -> WatchlistItem:
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def delete(self, item: WatchlistItem) -> None:
        self._db.delete(item)
        self._db.commit()

    def list_page(
        self,
        *,
        status: str | None,
        sort: str,
        page: int,
        page_size: int,
    ) -> tuple[list[WatchlistItem], int]:
        filters = []
        if status:
            filters.append(WatchlistItem.status == status)

        descending = sort.startswith("-")
        sort_key = sort.lstrip("-")
        column = _SORT_COLUMNS.get(sort_key, WatchlistItem.created_at)
        order = column.desc() if descending else column.asc()

        count_stmt: Select[tuple[int]] = select(func.count()).select_from(WatchlistItem)
        stmt = select(WatchlistItem)
        if filters:
            count_stmt = count_stmt.where(*filters)
            stmt = stmt.where(*filters)

        total = self._db.scalar(count_stmt) or 0
        offset = (page - 1) * page_size
        rows = list(self._db.scalars(stmt.order_by(order).offset(offset).limit(page_size)).all())
        return rows, total
