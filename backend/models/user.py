# Database schema

from sqlalchemy import (
    Column,
    Text,
    String,
    DateTime,
    Boolean,
    Enum,
    Float,
    Integer,
    ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
from .umixin import AppBase
import enum


class GenderEnum(str, enum.Enum):
    Male = "Male"
    Female = "Female"


class User(AppBase):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False)
    is_verified = Column(Boolean, default=False)

    profile = relationship("Profile", uselist=False, back_populates="user")
    vital_signs = relationship("VitalSign", back_populates="user")
    daily_logs = relationship("DailyLog", back_populates="user")
    goals = relationship("Goal", back_populates="user")


class Profile(AppBase):
    __tablename__ = "profile"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False)
    birthday = Column(DateTime, default=datetime(1940, 1, 1))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    body_fat_percent = Column(Float)
    gender = Column(Enum(GenderEnum, native_enum=False), nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship("User", back_populates="profile")


class VitalSign(AppBase):
    __tablename__ = "vital_signs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    systolic_bp = Column(Integer, nullable=False)
    diastolic_bp = Column(Integer, nullable=False)
    pre_glucose = Column(Integer)
    post_glucose = Column(Integer)
    heart_rate = Column(Integer, nullable=False)
    temperature_celsius = Column(Float)
    spo2 = Column(Integer)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship("User", back_populates="vital_signs")


class DailyLog(AppBase):
    __tablename__ = "daily_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    steps = Column(Integer)
    medication = Column(Boolean, default=False)
    meals_text = Column(Text)
    appetite_level = Column(Integer)
    bowel_status = Column(Text)
    mood_rate = Column(Integer)
    notes = Column(Text)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship("User", back_populates="daily_logs")


class Goal(AppBase):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    goal_text = Column(Text, nullable=False, default="Be Happy & Be Healthy!")
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )

    user = relationship("User", back_populates="goals")
