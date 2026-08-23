"""Human-written translations of source content.

The rest of this codebase stores official material in the language Monash
published it in, and the interface translates only its own chrome. That is the
right default and it is still the default: nothing here translates anything by
itself, and no model is involved.

What this table adds is a place to put a translation that a person wrote and a
person checked, so a Chinese-reading student can read a Handbook overview or an
official page in Chinese without the platform having invented the words.

Three things make that safe enough to show:

* **A translation is stored against the hash of the English it was made from.**
  When Monash edits the page, the hash moves and the translation is marked
  stale rather than quietly continuing to speak for text that no longer exists.
* **The original is always one click away**, and every translated block says it
  is an unofficial translation. We are not claiming Monash said this in Chinese.
* **Machine and human rows are kept apart.** ``provenance`` says which is
  which, the human row wins when both exist, and the page says which one the
  reader is looking at. A machine translation is useful and it is not the same
  claim as a checked one, so it is not presented as one.

The domain terms are not left to the machine either: ``app/knowledge/glossary.py``
holds the ones a wrong rendering would cost a student money or a semester -
census date, hurdle, WAM, credit points - and they are substituted before the
translator sees the sentence and put back afterwards.

The unit of storage is a *string map*, not a parallel copy of the document:
``data = {"strings": {"<english>": "<中文>"}}``, applied by exact match when the
page is serialised. Authoring a flat list of sentences is something a person can
actually review, and it survives Monash re-ordering a page, which a parallel
document tree does not.
"""
from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

# Scopes a translation can attach to. ``global`` is for the boilerplate the
# Handbook repeats verbatim across thousands of units - translating "Assessment
# details may change..." once covers every unit that carries it.
OFFICIAL_PAGE = "official_page"
UNIT = "unit"
# The curated FAQ is our own writing rather than a quotation, so translating it
# raises none of the questions the rest of this file exists to answer. It lives
# here anyway: one place to look for "what has Chinese and what does not" beats
# two, and the FAQ shows up beside the pages it summarises.
FAQ_ENTRY = "faq_entry"
GLOBAL = "global"
TARGET_TYPES = (OFFICIAL_PAGE, UNIT, FAQ_ENTRY, GLOBAL)

DRAFT = "draft"
PUBLISHED = "published"

# Who wrote it. A human row and a machine row can both exist for one target;
# the human one wins on read, so translating a page by hand later simply takes
# over from the machine without anybody deleting anything.
HUMAN = "human"
MACHINE = "machine"
PROVENANCES = (HUMAN, MACHINE)


class ContentTranslation(Base):
    __tablename__ = "content_translations"
    __table_args__ = (
        UniqueConstraint(
            "locale", "target_type", "target_key", "field", "provenance",
            name="uq_content_translations_target",
        ),
        # The lookup is always "everything for this page in this language", so
        # the index matches that shape rather than the columns' declared order.
        Index(
            "ix_content_translations_lookup",
            "target_type", "target_key", "locale", "status",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    locale: Mapped[str] = mapped_column(String(8))
    target_type: Mapped[str] = mapped_column(String(32))
    # An official page slug, a unit code, or the name of a global string set.
    target_key: Mapped[str] = mapped_column(String(120))
    # 'title', 'summary', 'overview', 'body', ...
    field: Mapped[str] = mapped_column(String(64))

    # Scalar fields use ``text``; string maps use ``data``. Exactly one is set.
    text: Mapped[str | None] = mapped_column(Text)
    data: Mapped[dict | None] = mapped_column(JSONB)

    # The content hash of the source this was translated from. A mismatch means
    # the source moved on and the reader has to be told.
    source_hash: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default=PUBLISHED)
    provenance: Mapped[str] = mapped_column(String(16), default=HUMAN)
    # Free text: a person's name, or the name of the batch it came in with.
    translator: Mapped[str | None] = mapped_column(String(120))
    note: Mapped[str | None] = mapped_column(Text)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
