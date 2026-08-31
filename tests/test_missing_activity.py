import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_github_skills_activity_exists():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert "GitHub Skills" in activities
    assert activities["GitHub Skills"]["max_participants"] >= 1


def test_students_can_signup_for_github_skills():
    response = client.post(
        "/activities/GitHub%20Skills/signup?email=student@mergington.edu"
    )
    assert response.status_code == 200
    assert "Signed up student@mergington.edu for GitHub Skills" in response.json()["message"]
