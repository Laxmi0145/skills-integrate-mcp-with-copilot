from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    schedule = Column(String)
    max_participants = Column(Integer)

    participants = relationship("Participant", back_populates="activity", cascade="all, delete-orphan")


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"))

    activity = relationship("Activity", back_populates="participants")
