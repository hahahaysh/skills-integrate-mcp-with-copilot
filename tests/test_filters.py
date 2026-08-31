import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_filters_and_search_are_available_in_activity_data():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()

    first_activity = next(iter(activities.values()))
    assert "category" in first_activity

    for activity in activities.values():
        assert "date" in activity


def test_activity_listing_supports_sorting_and_filtering_logic():
    response = client.get("/activities?sort=name&search=Club")
    assert response.status_code == 200

    items = response.json()
    assert items
    assert all("Club" in item["name"] or "club" in item["name"].lower() for item in items)
    assert items == sorted(items, key=lambda item: item["name"])
