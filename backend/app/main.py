"""Monash Hub API.

A modular monolith on purpose: one FastAPI app, one PostgreSQL database, no
message broker and no model provider. Everything the MVP promises is either a
database query or a template, so the extra moving parts would only be cost.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import ask, auth, community, exchange, guides, health, search, units
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
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

for module in (units, search, ask, guides, community, auth, exchange):
    app.include_router(module.router, prefix=settings.api_prefix)


@app.get("/api")
def api_root() -> dict:
    return {
        "name": settings.app_name,
        "version": app.version,
        "docs": "/api/docs",
        "disclaimer": (
            "Monash Hub is an independent student information platform and is not "
            "affiliated with or endorsed by Monash University."
        ),
    }
