"""User model."""
from sqlalchemy import Column, String, Boolean, DateTime, Date, Numeric, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class User(Base):
    """User model for authentication and profile."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))

    # Profile data
    date_of_birth = Column(Date)
    gender = Column(String(20))  # 'male', 'female', 'other', 'prefer_not_to_say'
    height_cm = Column(Numeric(5, 2))
    weight_kg = Column(Numeric(5, 2))
    activity_level = Column(String(20))  # 'sedentary', 'lightly_active', etc.

    # Goals
    goal_type = Column(String(20))  # 'lose_weight', 'maintain_weight', 'gain_weight'
    daily_calorie_target = Column(Integer)
    protein_target_g = Column(Numeric(6, 2))
    carbs_target_g = Column(Numeric(6, 2))
    fats_target_g = Column(Numeric(6, 2))
    water_target_ml = Column(Integer, default=2000)

    # Metadata
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('height_cm > 0', name='positive_height'),
        CheckConstraint('weight_kg > 0', name='positive_weight'),
    )
