"""Exchange module placeholder.

Exchange data is maintained by a separate tracker/service. Rather than fork that
dataset into Monash Hub, the product exposes an entry point and keeps API-level
integration as a later stage - see docs/ROADMAP-STATUS.md.
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
