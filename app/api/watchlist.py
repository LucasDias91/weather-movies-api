from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.deps import get_watchlist_service
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistPage,
    WatchlistResponse,
    WatchlistStatus,
    WatchlistUpdate,
)
from app.services.errors import DuplicateWatchlistError, WatchlistItemNotFoundError
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get(
    "",
    summary="Listar watchlist",
    description="Lista filmes salvos com filtro por status, ordenação e paginação.",
    response_model=WatchlistPage,
)
def list_watchlist(
    status_filter: WatchlistStatus | None = Query(None, alias="status"),
    sort: str = Query(
        "-created_at",
        description="Campo de ordenação: created_at, title, rating, id. Prefixo - para decrescente.",
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistPage:
    items, total = service.list_page(
        status=status_filter,
        sort=sort,
        page=page,
        page_size=page_size,
    )
    return WatchlistPage(
        items=[WatchlistResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    summary="Salvar filme na watchlist",
    description="Persiste um filme recomendado na lista do utilizador.",
    response_model=WatchlistResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_watchlist_item(
    payload: WatchlistCreate,
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistResponse:
    try:
        item = service.create(payload)
    except DuplicateWatchlistError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return WatchlistResponse.model_validate(item)


@router.put(
    "/{item_id}",
    summary="Atualizar status ou nota",
    description="Atualiza status (quero_assistir / assistido) e/ou nota do item.",
    response_model=WatchlistResponse,
)
def update_watchlist_item(
    item_id: int,
    payload: WatchlistUpdate,
    service: WatchlistService = Depends(get_watchlist_service),
) -> WatchlistResponse:
    try:
        item = service.update(item_id, payload)
    except WatchlistItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return WatchlistResponse.model_validate(item)


@router.delete(
    "/{item_id}",
    summary="Remover da watchlist",
    description="Remove o filme da lista persistida.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_watchlist_item(
    item_id: int,
    service: WatchlistService = Depends(get_watchlist_service),
) -> Response:
    try:
        service.delete(item_id)
    except WatchlistItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
