from __future__ import annotations

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import dashboard, data, scheduling


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Intelligent Production Scheduling & Optimization System",
    version="0.1.0",
    description="Production scheduling, validation, optimization, and dashboard backend.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174",
        ).split(",")
        if origin.strip()
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.include_router(dashboard.router, prefix="/api")
app.include_router(data.router, prefix="/api")
app.include_router(scheduling.router, prefix="/api")


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Production Scheduling & Optimization System"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
