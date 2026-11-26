"""Monash Hub API.

A modular monolith on purpose: one FastAPI app, one PostgreSQL database, no
message broker and no model provider. Everything the MVP promises is either a
database query or a template, so the extra moving parts would only be cost.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import (
    ask,
    auth,
    community,
    courses,
    dates,
    exchange,
    fees,
    guides,
    health,
    marks,
    notifications,
    plan,
    profile,
    reviews,
    search,
    units,
)
from app.core.config import get_settings
from app.version import __version__

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

settings = get_settings()

# Refuse to serve rather than serve with forgeable sessions. Only the API
# checks this; the migration and crawler containers never sign anything.
if settings.environment == "production" and (problem := settings.secret_key_problem()):
    raise RuntimeError(f"Refusing to start: {problem}. Set SECRET_KEY in the environment.")

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Structured Monash Handbook data, indexed official pages and a public "
        "student community. No generative AI in this version by design."
    ),
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# /api/health sits outside the version prefix: the reverse proxy and the deploy
# script probe it, and neither should have to know about /v1.
app.include_router(health.router, prefix="/api")

_READONLY_MODULES = (units, courses, plan, search, guides, exchange, marks, dates, fees)
_INTERACTIVE_MODULES = (ask, community, auth, notifications, profile, reviews)

for module in _READONLY_MODULES:
    app.include_router(module.router, prefix=settings.api_prefix)

if not settings.cn_readonly_mode:
    for module in _INTERACTIVE_MODULES:
        app.include_router(module.router, prefix=settings.api_prefix)
else:
    _DISABLED_PREFIXES = tuple(
        f"{settings.api_prefix}/{segment}"
        for segment in (
            "community",
            "reviews",
            "ask",
            "assistant",
            "auth",
            "profile",
            "notifications",
            "search/missing",
            "upload",
        )
    )

    @app.middleware("http")
    async def block_disabled_readonly_routes(request: Request, call_next):
        path = request.url.path.rstrip("/")
        if any(path == p or path.startswith(f"{p}/") for p in _DISABLED_PREFIXES):
            return JSONResponse(
                status_code=403,
                content={"detail": "This endpoint is disabled in read-only mode."},
            )
        return await call_next(request)


@app.get("/api")
def api_root() -> dict:
    return {
        "name": settings.app_name,
        "version": app.version,
        "commit": settings.app_commit or None,
        "docs": "/api/docs",
        "disclaimer": (
            "Monash Hub is an independent student information platform and is not "
            "affiliated with or endorsed by Monash University."
        ),
    }
