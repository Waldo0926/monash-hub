"""POST /ask - the zero-AI question endpoint.

No model is called here and no key is needed. See app/search/router.py for why.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.search import router as query_router

router = APIRouter(tags=["ask"])


class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    year: int | None = None


@router.post("/ask")
def ask(payload: AskRequest, db: Session = Depends(get_db)) -> dict:
    year = payload.year or get_settings().current_academic_year
    return query_router.answer(db, payload.query, year=year)
