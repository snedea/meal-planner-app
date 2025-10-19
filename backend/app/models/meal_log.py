"""Meal logging and tracking models."""
from sqlalchemy import Column, String, Text, Date, Time, DateTime, Numeric, ForeignKey, CheckConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class MealLog(Base):
    """Meal log model for daily food tracking."""

    __tablename__ = "meal_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # What was logged (either food OR recipe, not both)
    food_id = Column(UUID(as_uuid=True), ForeignKey('foods.id', ondelete='SET NULL'))
    recipe_id = Column(UUID(as_uuid=True), ForeignKey('recipes.id', ondelete='SET NULL'))

    # Quantity consumed
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=False)

    # Calculated nutrition (denormalized for performance)
    calories = Column(Numeric(8, 2))
    protein_g = Column(Numeric(6, 2))
    carbs_g = Column(Numeric(6, 2))
    fats_g = Column(Numeric(6, 2))

    # When logged
    meal_type = Column(String(20), nullable=False)  # 'breakfast', 'lunch', 'dinner', 'snack'
    logged_date = Column(Date, nullable=False, index=True)
    logged_time = Column(Time)

    # Notes
    notes = Column(Text)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    food = relationship("Food")
    recipe = relationship("Recipe")

    __table_args__ = (
        CheckConstraint("meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')", name='valid_meal_type'),
        CheckConstraint('quantity > 0', name='positive_quantity'),
    )


class Favorite(Base):
    """User favorites for foods and recipes."""

    __tablename__ = "favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # What is favorited (either food OR recipe)
    food_id = Column(UUID(as_uuid=True), ForeignKey('foods.id', ondelete='CASCADE'))
    recipe_id = Column(UUID(as_uuid=True), ForeignKey('recipes.id', ondelete='CASCADE'))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    food = relationship("Food")
    recipe = relationship("Recipe")


class WaterLog(Base):
    """Water intake tracking."""

    __tablename__ = "water_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Amount
    amount_ml = Column(Integer, nullable=False)

    # When logged
    logged_date = Column(Date, nullable=False, index=True)
    logged_time = Column(Time)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint('amount_ml > 0', name='positive_amount'),
    )
