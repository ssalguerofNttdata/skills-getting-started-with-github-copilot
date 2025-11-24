import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
_initial = copy.deepcopy(activities)


def setup_function():
    # Reset in-memory activities before each test
    activities.clear()
    activities.update(copy.deepcopy(_initial))


def test_get_activities():
    setup_function()
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    # Check some known activity keys
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_adds_participant_and_reflects_in_get():
    setup_function()
    email = "tester@example.edu"
    activity_name = "Chess Club"

    path = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"
    r = client.post(path)
    assert r.status_code == 200
    j = r.json()
    assert "Signed up" in j.get("message", "")

    # Confirm the participant is in the in-memory data and in GET
    assert email in activities[activity_name]["participants"]
    r2 = client.get("/activities")
    assert r2.status_code == 200
    assert email in r2.json()[activity_name]["participants"]


def test_unregister_removes_participant():
    setup_function()
    email = "to_remove@example.edu"
    activity_name = "Chess Club"

    # Add participant first
    activities[activity_name]["participants"].append(email)
    assert email in activities[activity_name]["participants"]

    path = f"/activities/{quote(activity_name)}/unregister?email={quote(email)}"
    r = client.delete(path)
    assert r.status_code == 200
    j = r.json()
    assert "Unregistered" in j.get("message", "")

    # Confirm removal
    assert email not in activities[activity_name]["participants"]
    r2 = client.get("/activities")
    assert email not in r2.json()[activity_name]["participants"]
