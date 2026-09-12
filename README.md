# Weather Movies — Backend

API REST em **FastAPI** com SQLite (SQLAlchemy). Recomenda filmes com base no clima: consome **OpenWeatherMap** (API externa da nota), trata o resultado (clima → gêneros) e busca cartazes no **TMDB**. A watchlist é persistida localmente.

Camadas (igual ao FileManager): rotas (`app/api/`) → serviços (`app/services/`) → repositórios (`app/repositories/`). Modelos em `app/models/` e schemas em `app/schemas/`. As tabelas são criadas automaticamente no startup (`Base.metadata.create_all`).

## Início rápido com `start.bat` (Windows)

1. Copie `.env.example` para `.env` e preencha as chaves:

   - [OpenWeatherMap](https://openweathermap.org/api) — cadastro gratuito, rota usada: `GET /data/2.5/weather`
   - [TMDB](https://developer.themoviedb.org/) — cadastro gratuito (extra de criatividade)

2. Na pasta `weather-movies-api`, execute **`start.bat`**. O script cria `.venv`, instala `requirements.txt` e abre o Swagger.

## Se o `start.bat` não funcionar (execução manual)

Use Python 3.10+ a partir desta pasta (onde existem `app/` e `requirements.txt`).

```bash
python -m venv .venv
```

Ative o ambiente:

- **Windows:** `.venv\Scripts\activate`
- **Linux / macOS:** `source .venv/bin/activate`

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Documentação:

- Swagger: http://127.0.0.1:8000/swagger
- ReDoc: http://127.0.0.1:8000/redoc

Na primeira execução o SQLite `weather_movies.db` é criado automaticamente.

## Docker

```bash
docker build -t weather-movies-api .
docker run --rm -p 8000:8000 --env-file .env weather-movies-api
```

Swagger: http://127.0.0.1:8000/swagger

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `OPENWEATHER_API_KEY` | Chave da OpenWeatherMap (obrigatória para recomendações) | vazio |
| `TMDB_API_KEY` | Chave da TMDB (obrigatória para filmes) | vazio |
| `DATABASE_URL` | URL SQLAlchemy | `sqlite:///./weather_movies.db` |
| `HEAT_THRESHOLD_C` | Temperatura (°C) a partir da qual o gênero vira Ação | `32` |

## Endpoints

| Método | Rota | Uso |
|--------|------|-----|
| GET | `/api/recommendations?city=` | Clima + filmes mapeados |
| GET | `/api/watchlist` | Lista com filtro, ordenação e paginação |
| POST | `/api/watchlist` | Salvar filme |
| PUT | `/api/watchlist/{id}` | Atualizar status/nota |
| DELETE | `/api/watchlist/{id}` | Remover |

Mapeamento clima → gênero: chuva/tempestade → terror/thriller/drama; céu limpo → comédia/aventura; nublado → documentário/drama; neve → romance/família; neblina → mistério; calor extremo → ação.

CORS está configurado para desenvolvimento (`allow_origins=["*"]`).

## Estrutura

```
app/
  api/            # rotas HTTP (Swagger)
  core/           # configuração / .env
  db/             # engine, sessão, create_all
  models/         # tabelas SQLAlchemy
  repositories/   # acesso a dados
  schemas/        # Pydantic (entrada/saída)
  services/       # regras de negócio e clientes HTTP
  main.py         # FastAPI + lifespan
```
