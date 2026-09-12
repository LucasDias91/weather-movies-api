from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.recommendations import router as recommendations_router
from app.api.watchlist import router as watchlist_router
from app.db.database import init_db

OPENAPI_TAGS = [
    {
        "name": "recommendations",
        "description": (
            "GET que consulta a OpenWeatherMap, trata o clima (mapeamento para gêneros) "
            "e devolve filmes do TMDB. Não há redirect para as APIs externas."
        ),
    },
    {
        "name": "watchlist",
        "description": (
            "CRUD da lista de filmes persistida em SQLite. "
            "GET (filtro/ordenação/paginação), POST, PUT e DELETE."
        ),
    },
]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Weather Movies API",
    description=(
        "API secundária do MVP Plataforma A: recomenda filmes com base no clima. "
        "Consome OpenWeatherMap (API externa da nota) e TMDB, persiste a watchlist em SQLite. "
        "Tabelas são criadas automaticamente na inicialização."
    ),
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
    docs_url="/swagger",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommendations_router, prefix="/api")
app.include_router(watchlist_router, prefix="/api")
