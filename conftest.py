"""
Shared pytest fixtures.

Spins up a fresh in-memory SQLite database for each test and overrides the
app's get_db dependency so tests never touch the real kittenconnect.db.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models
from database import Base, get_db
from main import app


@pytest.fixture
def client():
    # In-memory DB shared across the connection pool for the duration of one test.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def signed_up_user(client):
    """Registers one user and returns their credentials."""
    payload = {
        "name": "Ada",
        "email": "ada@example.com",
        "password": "s3cret-pw",
        "location": "Addis Ababa",
    }
    client.post("/signup", json=payload)
    return payload


@pytest.fixture
def auth_headers(client, signed_up_user):
    """Logs the user in and returns a ready-to-use Authorization header."""
    resp = client.post(
        "/login",
        json={"email": signed_up_user["email"], "password": signed_up_user["password"]},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
