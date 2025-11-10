"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

from .db import init_db, SessionLocal
from .models import Activity, Participant

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Sample activities used to seed DB when empty
SAMPLE_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
}


def seed_db_if_empty():
    db = SessionLocal()
    try:
        count = db.query(Activity).count()
        if count == 0:
            for name, data in SAMPLE_ACTIVITIES.items():
                act = Activity(name=name,
                               description=data.get("description"),
                               schedule=data.get("schedule"),
                               max_participants=data.get("max_participants"))
                db.add(act)
                db.commit()
                # add participants
                for email in data.get("participants", []):
                    p = Participant(email=email, activity_id=act.id)
                    db.add(p)
                db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    # Initialize DB and seed sample data
    init_db()
    seed_db_if_empty()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    db = SessionLocal()
    try:
        activities = {}
        for act in db.query(Activity).all():
            participants = [p.email for p in act.participants]
            activities[act.name] = {
                "description": act.description,
                "schedule": act.schedule,
                "max_participants": act.max_participants,
                "participants": participants
            }
        return activities
    finally:
        db.close()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    db = SessionLocal()
    try:
        act = db.query(Activity).filter(Activity.name == activity_name).first()
        if not act:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Check if already signed up
        exists = db.query(Participant).filter(Participant.activity_id == act.id, Participant.email == email).first()
        if exists:
            raise HTTPException(status_code=400, detail="Student is already signed up")

        # Add participant
        p = Participant(email=email, activity_id=act.id)
        db.add(p)
        db.commit()
        return {"message": f"Signed up {email} for {activity_name}"}
    finally:
        db.close()


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    db = SessionLocal()
    try:
        act = db.query(Activity).filter(Activity.name == activity_name).first()
        if not act:
            raise HTTPException(status_code=404, detail="Activity not found")

        participant = db.query(Participant).filter(Participant.activity_id == act.id, Participant.email == email).first()
        if not participant:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        db.delete(participant)
        db.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
    finally:
        db.close()
