# Weather Movies — Backend

API REST em **FastAPI** com SQLite (SQLAlchemy). Recomenda filmes com base no clima: consome **OpenWeatherMap** (API externa da nota), trata o resultado (clima → gêneros) e busca cartazes no **TMDB**. A watchlist é persistida localmente.

Camadas (igual ao FileManager): rotas (`app/api/`) → serviços (`app/services/`) → repositórios (`app/repositories/`). Modelos em `app/models/` e schemas em `app/schemas/`. As tabelas são criadas automaticamente no startup (`Base.metadata.create_all`).

## Início rápido com `start.bat` (Windows)

1. Copie `.env.example` para `.env` e preencha as chaves:

   - [OpenWeatherMap](https://openweathermap.org/api) — cadastro gratuito, rota usada: `GET /data/2.5/weather`
   - [TMDB](https://developer.themoviedb.org/docs) — cadastro gratuito, rota usada: `GET /3/discover/movie`

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

## API externa documentada (TMDB)

A TMDB é a API externa dos filmes e dos cartazes. A API própria consulta, trata o resultado e devolve o JSON. Não há redirect para o site da TMDB.

- Serviço: [TMDB API](https://developer.themoviedb.org/docs)
- Licença: uso gratuito não comercial, com atribuição à TMDB. Uso comercial exige autorização. Termos: https://www.themoviedb.org/api-terms-of-use
- Cadastro da key: https://www.themoviedb.org/signup e, em seguida, https://www.themoviedb.org/settings/api
- Rota usada: `GET https://api.themoviedb.org/3/discover/movie`
- Cartazes: `https://image.tmdb.org/t/p/w500/{poster_path}`

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
| GET | `/api/locations?q=` | Sugestões de municípios brasileiros |
| GET | `/api/weather/icons/{icon}` | PNG do ícone do clima, servido pela API |
| GET | `/api/watchlist` | Lista com filtro, ordenação e paginação |
| POST | `/api/watchlist` | Salvar filme |
| PUT | `/api/watchlist/{id}` | Atualizar status/nota |
| DELETE | `/api/watchlist/{id}` | Remover |

## Critério de filme por clima

O gênero vem do campo `main` da OpenWeather, não de uma escala contínua de temperatura. Se a temperatura for igual ou maior que `HEAT_THRESHOLD_C` (padrão **32°C**), a sessão é só **Ação**, qualquer que seja o céu. Abaixo disso:

| Tempo (`main`) | Gêneros |
|----------------|---------|
| Chuva, garoa ou tempestade (`Rain`, `Drizzle`, `Thunderstorm`) | Terror, Thriller e Drama |
| Céu limpo (`Clear`) | Comédia e Aventura |
| Nublado (`Clouds`) | Documentário e Drama |
| Neve (`Snow`) | Romance e Família |
| Neblina, fumaça, névoa, areia ou poeira (`Mist`, `Smoke`, `Haze`, `Fog`, `Sand`, `Dust`) | Mistério |
| Cinzas (`Ash`) | Terror e Thriller |
| Rajada ou tornado (`Squall`, `Tornado`) | Ação e Thriller |
| Qualquer outro | Drama e Comédia |

Com esses gêneros, o TMDB devolve até 12 filmes, em pt-BR, ordenados por popularidade e sem conteúdo adulto. Quando há mais de um gênero, o filme precisa ter todos ao mesmo tempo.

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
