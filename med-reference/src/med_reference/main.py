import httpx2
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from med_reference import routers

app = FastAPI()
app.include_router(routers.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(httpx2.HTTPError)
async def condition_exception_handler(
    request: Request, exc: httpx2.HTTPError
) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={
            "detail": f"OLS unavailable {exc}",
        },
    )
