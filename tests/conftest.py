"""Shared fixtures for ScholarForge tests."""
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.dependencies import get_current_user, require_auth
from app.main import app
from app.models import Claim, Evidence, Note, Project, SavedResource, Theme, User
from app.models.outline_section import OutlineSection

# ── Canonical fake objects ──────────────────────────────────────────────────

FAKE_USER = User(
    id="u1",
    email="test@example.com",
    password_hash="$2b$12$fakehash",
)

FAKE_PROJECT = Project(
    id="p1",
    user_id="u1",
    name="Test Project",
    research_question="What is AI?",
    created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
)

FAKE_SOURCE = SavedResource(
    id="s1",
    project_id="p1",
    title="Test Paper",
    authors=["Alice", "Bob"],
    year=2023,
    source="manual",
    added_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
)

FAKE_EVIDENCE = Evidence(
    id="e1",
    project_id="p1",
    source_id="s1",
    user_id="u1",
    quote="Important finding here.",
    created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
)

FAKE_NOTE = Note(
    id="n1",
    project_id="p1",
    user_id="u1",
    title="My Note",
    body="Note body text.",
    created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
)

FAKE_THEME = Theme(
    id="t1",
    project_id="p1",
    user_id="u1",
    name="Test Theme",
    created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
)

FAKE_CLAIM = Claim(
    id="c1",
    project_id="p1",
    user_id="u1",
    statement="AI will change research.",
    created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
)

FAKE_SECTION = OutlineSection(
    id="sec1",
    project_id="p1",
    user_id="u1",
    title="Introduction",
    order_index=0,
)

# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db):
    """Authenticated test client."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[require_auth] = lambda: FAKE_USER
    yield TestClient(app, follow_redirects=False)
    app.dependency_overrides.clear()


@pytest.fixture
def anon_client(mock_db):
    """Unauthenticated client — get_current_user returns None."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: None
    yield TestClient(app, follow_redirects=False)
    app.dependency_overrides.clear()


@pytest.fixture
def authed_anon_client(mock_db):
    """Client where get_current_user returns FAKE_USER (auth page redirect tests)."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_current_user] = lambda: FAKE_USER
    yield TestClient(app, follow_redirects=False)
    app.dependency_overrides.clear()
