import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Preserve original in-memory activities between tests
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    email = "testuser@mergington.edu"
    path = f"/activities/{quote('Chess Club')}/signup?email={quote(email)}"
    resp = client.post(path)
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    # michael@mergington.edu is already a participant in the initial data
    email = "michael@mergington.edu"
    path = f"/activities/{quote('Chess Club')}/signup?email={quote(email)}"
    resp = client.post(path)
    assert resp.status_code == 400


def test_remove_participant_success():
    email = "michael@mergington.edu"
    path = f"/activities/{quote('Chess Club')}/participants?email={quote(email)}"
    resp = client.delete(path)
    assert resp.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_remove_participant_not_found():
    email = "not-a-user@x.com"
    path = f"/activities/{quote('Chess Club')}/participants?email={quote(email)}"
    resp = client.delete(path)
    assert resp.status_code == 404