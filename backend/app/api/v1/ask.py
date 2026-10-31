"""POST /ask - the zero-AI question endpoint.

No model is called here and no key is needed. See app/search/router.py for why.
"""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import requested_locale
from app.core import throttle, wxbot
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
    # The campus the reader is at, when the caller knows it (a group chat bot
    # for Monash Malaysia does). Official pages for that campus come first; a
    # campus named in the question still wins.
    campus: Literal["australia", "malaysia"] | None = None


@router.post("/ask")
def ask(
    payload: AskRequest,
    locale: str | None = Depends(requested_locale),
    db: Session = Depends(get_db),
) -> dict:
    year = payload.year or get_settings().current_academic_year
    return query_router.answer(
        db, payload.query, year=year, locale=locale, context_unit=payload.unit_code,
        campus=payload.campus)


class BotRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    # The browser's own random id, so the bot can tell one reader from another.
    visitor: str = Field(min_length=1, max_length=64)


@router.post("/assistant/bot")
def ask_bot(payload: BotRequest, request: Request, db: Session = Depends(get_db)) -> dict:
    """The 马莫百科 bot's answer to the same question, for the Ask panel.

    ``available`` is false when the bot is not configured or did not answer,
    and the panel then shows only /ask's answer. A ``reply`` of null with a
    route of ``miss`` means the bot had nothing; the panel points the reader at
    the 公众号, where the owner can answer later.
    """
    if not wxbot.configured():
        return {"available": False, "route": None, "reply": None}
    address = throttle.client_address(request)
    try:
        throttle.check(db, throttle.BOT_QUESTIONS_PER_ADDRESS, address)
    except throttle.Throttled as limited:
        db.rollback()
        raise HTTPException(
            status_code=429,
            detail="Too many questions. Wait a moment and try again.",
            headers={"Retry-After": str(limited.retry_after_seconds)},
        ) from limited
    throttle.record(db, throttle.BOT_QUESTIONS_PER_ADDRESS, address)
    # Committed before the call: the bot can take seconds, and the advisory
    # lock check() took would hold every other question from this address.
    db.commit()
    answer = wxbot.ask(payload.query.strip(), payload.visitor.strip())
    if answer is None:
        return {"available": False, "route": None, "reply": None}
    return {"available": True, "route": answer.route, "reply": answer.reply}
