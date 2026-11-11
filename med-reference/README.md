# med-reference

[![CI](https://github.com/FirstAM/med-ai-lab/actions/workflows/med-reference.yml/badge.svg)](https://github.com/FirstAM/med-ai-lab/actions/workflows/med-reference.yml)

A small async FastAPI service for looking up diseases in the [Mondo Disease Ontology](https://mondo.monarchinitiative.org/) ontology. Data comes from the [EBI Ontology Lookup Service (OLS)](https://www.ebi.ac.uk/ols4/).

## What it demonstrates

- **Async I/O**: routes call OLS through `httpx2.AsyncClient`, so slow upstream calls do not block other requests.
- **Upstream failure handling**: any `httpx2.HTTPError` (network error, timeout, 4xx/5xx from OLS) is turned into `502 Bad Gateway` by a single exception handler.
- **Strict typing and linting**: `mypy --strict` and `ruff` (lint and format) pass on the whole package.
- **Tests without network**: routes are tested with FastAPI `TestClient` and `monkeypatch`; the OLS client is tested with `httpx2.MockTransport`, including the query parameters it sends.
- **Reproducible dependencies**: `uv` with a committed `uv.lock`; CI and Docker install with `--locked`.
- **Production image**: multi-stage Docker build; the final image contains only the virtual environment and runs as a non-root user.
- **CI**: GitHub Actions runs lint, format check, type check and tests on every change to this project.

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

```
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
