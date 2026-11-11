# med-reference

[![CI](https://github.com/FirstAM/med-ai-lab/actions/workflows/med-reference.yml/badge.svg)](https://github.com/FirstAM/med-ai-lab/actions/workflows/med-reference.yml)

A lightweight async FastAPI service for looking up diseases by code or text.

Disease terms come from the [Mondo Disease Ontology](https://mondo.monarchinitiative.org/), served through the [EBI Ontology Lookup Service (OLS)](https://www.ebi.ac.uk/ols4/) [API](https://www.ebi.ac.uk/ols4/api-docs).

**Stack:** `Python 3.12`, `FastAPI`, `httpx2`, `Pydantic`, `pytest`, `mypy (strict)`, `ruff`, `uv`, `Docker`.

## API

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/conditions/{code}` | Find a disease by its MONDO code |
| `POST` | `/conditions/search` | Search diseases by text |

Interactive docs are available at `/docs` when the service is running.

```bash
curl http://127.0.0.1:8000/conditions/MONDO:0004979
# {"code":"MONDO:0004979","name":"asthma"}

curl -X POST http://127.0.0.1:8000/conditions/search \
  -H "Content-Type: application/json" \
  -d '{"query": "asthma", "limit": 2}'
# [{"code":"MONDO:...","name":"..."}, ...]
```

| Status | When |
|---|---|
| `404` | No disease with this code |
| `422` | Invalid request, e.g. `limit` outside 1–50 |
| `502` | OLS is unavailable or returned an error |

## Run locally

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run fastapi dev
```

The service starts at http://127.0.0.1:8000.

## Run in Docker

```bash
docker build -t med-reference .
docker run --rm -p 8000:8000 med-reference
```

## Checks

```bash
uv run pytest --cov=med_reference --cov-report=term-missing
uv run mypy src
uv run ruff check src
uv run ruff format --check src
```

## Project structure

```__
med-reference/
├── src/med_reference/
│   ├── main.py      # app, /health, OLS error handler
│   ├── routers.py   # /conditions routes
│   ├── ols.py       # OLS client, no FastAPI dependency
│   └── schemas.py   # Pydantic models
├── tests/
├── Dockerfile
├── pyproject.toml
└── uv.lock
```

## Design notes

- `ols.py` knows nothing about FastAPI. Routes depend on it through module attributes, so tests replace it without touching the network.
- Error mapping lives in one place (`main.py`) instead of `try/except` in every route.
- The project is installed into the virtual environment with `--no-editable` in Docker, so the final stage copies only `.venv` and no source tree.

## Possible improvements

- Reuse one `AsyncClient` for the app lifetime instead of creating it per request.
- Log upstream errors server-side and return a generic `502` message to clients.
- Retry transient OLS failures.
