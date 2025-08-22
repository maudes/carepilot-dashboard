# Database schema

from sqlalchemy import (
    Column,
    Text,
    String,
    Date,
    Boolean,
    Enum,
    Float,
    Integer,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import date
from uuid import uuid4
from .umixin import AppBase
import enum


class GenderEnum(str, enum.Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"


class User(AppBase):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False)
    is_verified = Column(Boolean, default=False)

    profile = relationship("Profile", uselist=False, back_populates="user")
    # vital_sign = relationship("VitalSign", back_populates="user")
    # daily_log = relationship("DailyLog", back_populates="user")
    goal = relationship("Goal", back_populates="user")
    daily_record = relationship(
        "DailyRecord",
        back_populates="user",
        order_by="DailyRecord.record_date"
    )
    # userlist=False means 1 to 1 instead of 1 to many


class Profile(AppBase):
    __tablename__ = "profile"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(50), nullable=False, default="User")
    birthday = Column(Date, default=date(1940, 1, 1))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    body_fat_percent = Column(Float)
    # gender = Column(String(10), nullable=False)
    gender = Column(
        Enum(GenderEnum, native_enum=False),
        nullable=False,
        default=GenderEnum.Other
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
        unique=True,
    )

    user = relationship("User", back_populates="profile")
    '''
    __table_args__ = (
        CheckConstraint("gender IN ('Male', 'Female')", name="gender_check"),
    )
    '''


class VitalSign(AppBase):
    __tablename__ = "vital_sign"

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
        ForeignKey("user.id"),
        nullable=False,
    )

    # user = relationship("User", back_populates="vital_sign")
    daily_record = relationship(
        "DailyRecord",
        back_populates="vital_sign",
        uselist=False,
    )


class DailyLog(AppBase):
    __tablename__ = "daily_log"

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
        ForeignKey("user.id"),
        nullable=False,
    )

    # user = relationship("User", back_populates="daily_log")
    daily_record = relationship(
        "DailyRecord",
        back_populates="daily_log",
        uselist=False,
    )


class Goal(AppBase):
    __tablename__ = "goal"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    goal_text = Column(Text, nullable=False, default="Be Happy & Be Healthy!")
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
        unique=True,
    )

    user = relationship("User", back_populates="goal")


class DailyRecord(AppBase):
    __tablename__ = "daily_record"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    record_date = Column(Date, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)

    vital_sign_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vital_sign.id"),
        nullable=False,
        unique=True
    )
    daily_log_id = Column(
        UUID(as_uuid=True),
        ForeignKey("daily_log.id"),
        nullable=False,
        unique=True
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "record_date",
            name="unique_user_daily_record"
        ),
    )

    user = relationship("User", back_populates="daily_record")
    vital_sign = relationship(
        "VitalSign",
        back_populates="daily_record",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )
    daily_log = relationship(
        "DailyLog",
        back_populates="daily_record",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )
