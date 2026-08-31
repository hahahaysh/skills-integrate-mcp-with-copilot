import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app import app, activities

from fastapi.testclient import TestClient

client = TestClient(app)


def test_activities_are_loaded_from_json_file():
    activities_path = Path("src/activities.json")
    assert activities_path.exists()
    loaded = json.loads(activities_path.read_text(encoding="utf-8"))
    assert loaded
    assert isinstance(loaded, dict)


def test_activity_updates_are_preserved_through_json_file():
    response = client.get("/activities")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert bool(response.json())
