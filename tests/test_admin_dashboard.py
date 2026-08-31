import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_admin_login_success():
    response = client.post(
        "/admin/login",
        json={"username": "teacher", "password": "teacher123"},
    )
    assert response.status_code == 200
    assert "token" in response.json()


def test_admin_can_create_activity():
    login = client.post(
        "/admin/login",
        json={"username": "teacher", "password": "teacher123"},
    )
    token = login.json()["token"]

    response = client.post(
        "/admin/activities",
        json={
            "name": "Robotics Club",
            "description": "Build robots and compete in local challenges",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["alice@mergington.edu"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Robotics Club"
    assert body["participants"] == ["alice@mergington.edu"]


def test_admin_activity_listing_includes_created_activity():
    login = client.post(
        "/admin/login",
        json={"username": "teacher", "password": "teacher123"},
    )
    token = login.json()["token"]

    response = client.get(
        "/admin/activities",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert "Robotics Club" in names
