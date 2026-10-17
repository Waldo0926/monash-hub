"""POST /ask - the zero-AI question endpoint.

No model is called here and no key is needed. See app/search/router.py for why.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import requested_locale
from app.core.config import get_settings
from app.core.db import get_db
from app.search import router as query_router

router = APIRouter(tags=["ask"])


class AskRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    year: int | None = None
    # The unit page the question was asked from. It only fills in a unit the
    # question itself does not name, so "How good is this unit?" on the FIT2102
    # page is a question about FIT2102.
    unit_code: str | None = Field(default=None, max_length=16)


@router.post("/ask")
def ask(
    payload: AskRequest,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    year = payload.year or get_settings().current_academic_year
    return query_router.answer(
        db, payload.query, year=year, locale=locale, context_unit=payload.unit_code)
