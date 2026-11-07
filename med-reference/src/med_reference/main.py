from typing import Any
from unittest import case

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from med_reference import conditions

app = FastAPI()
app.include_router(conditions.router)

@app.get("/health")
async def health():
    return {"status": "ok"}





