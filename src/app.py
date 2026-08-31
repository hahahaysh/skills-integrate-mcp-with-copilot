"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import json
import os
import secrets
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

security = HTTPBearer(auto_error=False)


def load_teachers():
    teachers_path = Path(__file__).with_name("teachers.json")
    with teachers_path.open("r", encoding="utf-8") as file:
        return json.load(file)


TEACHERS = load_teachers()
ACTIVE_TOKENS = {}


def load_activities():
    activities_path = Path(__file__).with_name("activities.json")
    with activities_path.open("r", encoding="utf-8") as file:
        return json.load(file)


activities = load_activities()


def persist_activities():
    activities_path = Path(__file__).with_name("activities.json")
    with activities_path.open("w", encoding="utf-8") as file:
        json.dump(activities, file, indent=2)
        file.write("\n")


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    token = credentials.credentials
    username = ACTIVE_TOKENS.get(token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    return username


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(sort: str | None = None, search: str | None = None, category: str | None = None):
    if sort is None and search is None and category is None:
        return activities

    items = []
    for name, details in activities.items():
        item = {"name": name, **details}

        if category and item.get("category", "").lower() != category.lower():
            continue

        if search:
            query = search.lower()
            haystack = " ".join([
                item["name"],
                item.get("description", ""),
                item.get("schedule", ""),
                item.get("category", "")
            ]).lower()
            if query not in haystack:
                continue

        items.append(item)

    if sort == "name":
        items.sort(key=lambda item: item["name"].lower())
    elif sort == "date":
        items.sort(key=lambda item: item.get("date", ""))
    elif sort == "category":
        items.sort(key=lambda item: item.get("category", "").lower())

    return items


@app.post("/admin/login")
def login_admin(payload: dict):
    username = (payload or {}).get("username")
    password = (payload or {}).get("password")

    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    if TEACHERS.get(username) != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = secrets.token_urlsafe(32)
    ACTIVE_TOKENS[token] = username
    return {"token": token, "username": username}


@app.get("/admin/activities")
def get_admin_activities(username: str = Depends(get_current_admin)):
    return [
        {"name": name, **details}
        for name, details in activities.items()
    ]


@app.post("/admin/activities", status_code=status.HTTP_201_CREATED)
def create_activity(payload: dict, username: str = Depends(get_current_admin)):
    name = (payload or {}).get("name")
    description = (payload or {}).get("description")
    schedule = (payload or {}).get("schedule")
    max_participants = (payload or {}).get("max_participants")
    participants = (payload or {}).get("participants", [])

    if not name or not description or not schedule or not max_participants:
        raise HTTPException(status_code=400, detail="Name, description, schedule, and max_participants are required")

    if name in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")

    activities[name] = {
        "description": description,
        "schedule": schedule,
        "max_participants": int(max_participants),
        "participants": participants,
        "category": "General",
        "date": "2026-09-15",
    }
    persist_activities()

    return {"name": name, **activities[name]}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(
            status_code=400,
            detail="Activity is full"
        )

    # Add student
    activity["participants"].append(email)
    persist_activities()
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    persist_activities()
    return {"message": f"Unregistered {email} from {activity_name}"}
