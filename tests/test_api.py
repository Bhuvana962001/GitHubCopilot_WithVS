import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Backup the in-memory activities and restore after each test to keep tests isolated."""
    orig = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(orig))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # ensure one expected activity exists
    assert "Chess Club" in data


def test_signup_and_unregister():
    activity = "Chess Club"
    email = "testuser@example.com"

    # ensure not present
    resp = client.get("/activities")
    before = resp.json()[activity]["participants"][:]
    assert email not in before

    # signup
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    resp = client.get("/activities")
    after = resp.json()[activity]["participants"]
    assert email in after
    assert len(after) == len(before) + 1

    # signing up again should fail
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 400

    # unregister
    resp = client.post(f"/activities/{quote(activity)}/unregister", params={"email": email})
    assert resp.status_code == 200
    resp = client.get("/activities")
    final = resp.json()[activity]["participants"]
    assert email not in final
