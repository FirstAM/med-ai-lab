from typing import Any
from unittest import case

import httpx2
from fastapi import FastAPI, HTTPException
from fastapi import Request
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from med_reference import routers
from med_reference.ols import EBI_URL

app = FastAPI()
app.include_router(routers.router)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.exception_handler(httpx2.HTTPError)
async def condition_exception_handler(request: Request, exc: httpx2.HTTPError):
    return JSONResponse(
        status_code=502,
        content={"message": "OLS unavailable", "detail": f"{exc.__cause__}"},
    )


