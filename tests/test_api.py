# pylint: disable=missing-function-docstring, missing-module-docstring

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import get_db # pylint: disable=import-error
from models import Base # pylint: disable=import-error
from api.api import app # pylint: disable=import-error

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def run_around_tests():
    # Clear the database before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "This is the application backend."


def test_incorrect_method():
    response = client.patch("/", json={})
    assert response.status_code == 405


def test_incorrect_header():
    response = client.post("/", headers={"Content-Type": "text/plain"}, content="test")
    assert response.status_code == 415


def test_create_note():
    response = client.post(
        "/notes",
        json={"title": "Test Note", "content": "This is a test", "creator": "Tester"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test"
    assert data["creator"] == "Tester"


def test_create_note_error():
    response = client.post(
        "/notes",
        json={"title": "Test Note", "creator": "Tester"},
    )
    assert response.status_code == 422


def test_get_notes_all():
    client.post(
        "/notes",
        json={"title": "Note1", "content": "Hello", "creator": "Tester"},
    )
    response = client.get("/notes")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Note1"


def test_read_note():
    create_resp = client.post(
        "/notes",
        json={"title": "MyNote", "content": "Content", "creator": "Tester"},
    )
    note_id = create_resp.json()["id"]

    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "MyNote"


def test_update_note():
    create_resp = client.post(
        "/notes",
        json={"title": "OldTitle", "content": "OldContent", "creator": "Tester"},
    )
    note_id = create_resp.json()["id"]

    response = client.put(
        f"/notes/{note_id}",
        json={"title": "NewTitle", "content": "NewContent", "creator": "Tester"},
    )
    assert response.status_code == 200
    assert "successfully updated" in response.json()["message"]


def test_delete_note():

    create_resp = client.post(
        "/notes",
        json={"title": "ToDelete", "content": "bye", "creator": "Tester"},
    )
    note_id = create_resp.json()["id"]

    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 200
    assert "successfully deleted" in response.json()["message"]

    # Check it's gone
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 404
