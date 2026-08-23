"""Test fixtures.

Parser and router tests need no database and always run. API tests need a real
PostgreSQL because the schema leans on tsvector, trigram and array types that
SQLite cannot fake; they are skipped unless ``TEST_DATABASE_URL`` is set, and CI
sets it.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def handbook_html():
    def _load(code: str) -> str:
        return (FIXTURES / "handbook" / f"{code}.html").read_text()

    return _load


@pytest.fixture(scope="session")
def official_html():
    def _load(name: str) -> str:
        return (FIXTURES / "official" / f"{name}.html").read_text()

    return _load


@pytest.fixture(scope="session")
def database_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is not set")
    return url


@pytest.fixture(scope="session")
def engine(database_url):
    import app.models  # noqa: F401
    from app.core.db import Base
    from sqlalchemy import create_engine, text

    eng = create_engine(database_url)
    with eng.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    Base.metadata.drop_all(eng)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def db(engine):
    """A clean database per test.

    Truncating is cheaper than recreating the schema, and it keeps each test
    honest about what it inserted rather than inheriting rows from its
    neighbours.
    """
    from app.core.db import Base
    from sqlalchemy import text
    from sqlalchemy.orm import sessionmaker

    tables = ", ".join(f'"{name}"' for name in Base.metadata.tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))

    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def mailbox(monkeypatch):
    """Capture outbound mail instead of sending it, and expose the codes.

    Registration and password reset are only testable end to end if the test can
    read the code, and reading it out of the captured message is the same path a
    real user takes - no test-only bypass in the application itself.
    """
    import re

    from app.core import email as email_module

    sent: list[email_module.Message] = []

    def capture(self, message):
        sent.append(message)

    monkeypatch.setattr(email_module.Emailer, "send", capture)

    class Mailbox:
        messages = sent

        def code_for(self, address: str) -> str:
            for message in reversed(sent):
                if message.to.lower() == address.lower():
                    found = re.search(r"\b(\d{6})\b", message.text)
                    if found:
                        return found.group(1)
            raise AssertionError(f"no verification code was sent to {address}")

    return Mailbox()


@pytest.fixture
def client(engine, db):
    from app.core.db import get_db
    from app.main import app
    from fastapi.testclient import TestClient

    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
