"""Exchange module placeholder.

The Monash Abroad Tracker already owns this data and keeps running on its own
box. Rather than fork it, the MVP publishes an entry point and states plainly
that integration is a later stage - see docs/ROADMAP-STATUS.md.
"""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/exchange", tags=["exchange"])


@router.get("")
def exchange_overview() -> dict:
    return {
        "status": "planned",
        "stage": "Stage 5 - Knowledge Expansion",
        "summary": (
            "Exchange data currently lives in the Monash Abroad Tracker. The Hub will "
            "integrate it through an API rather than duplicating the dataset."
        ),
        "topics": [
            {"key": "eligibility", "label": "Eligibility and application"},
            {"key": "partners", "label": "Partner institutions"},
            {"key": "credit", "label": "Credit transfer and course mapping"},
        ],
    }
