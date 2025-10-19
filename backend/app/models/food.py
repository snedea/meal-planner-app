"""Food and nutrition models."""
from sqlalchemy import Column, String, Boolean, DateTime, Text, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Food(Base):
    """Food model for master food database."""

    __tablename__ = "foods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    brand = Column(String(255))
    barcode = Column(String(50), index=True)

    # Source tracking
    source = Column(String(20), nullable=False)  # 'openfoodfacts', 'usda', 'custom'
    source_id = Column(String(100))

    # Metadata
    description = Column(Text)
    is_verified = Column(Boolean, default=False)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    nutrition = relationship("NutritionInfo", back_populates="food", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("source IN ('openfoodfacts', 'usda', 'custom')", name='valid_source'),
    )


class NutritionInfo(Base):
    """Nutrition information for foods."""

    __tablename__ = "nutrition_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    food_id = Column(UUID(as_uuid=True), ForeignKey('foods.id', ondelete='CASCADE'), nullable=False, index=True)

    # Serving information
    serving_size = Column(Numeric(10, 2), nullable=False)
    serving_unit = Column(String(50), nullable=False)  # 'g', 'ml', 'oz', 'cup', etc.
    servings_per_container = Column(Numeric(6, 2))

    # Macronutrients (per serving)
    calories = Column(Numeric(8, 2), nullable=False)
    protein_g = Column(Numeric(6, 2), default=0)
    carbs_g = Column(Numeric(6, 2), default=0)
    fats_g = Column(Numeric(6, 2), default=0)

    # Additional macros
    fiber_g = Column(Numeric(6, 2))
    sugar_g = Column(Numeric(6, 2))
    saturated_fat_g = Column(Numeric(6, 2))
    trans_fat_g = Column(Numeric(6, 2))
    cholesterol_mg = Column(Numeric(6, 2))
    sodium_mg = Column(Numeric(6, 2))

    # Micronutrients (JSONB for flexibility)
    micronutrients = Column(JSONB)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    food = relationship("Food", back_populates="nutrition")

    __table_args__ = (
        CheckConstraint('serving_size > 0', name='positive_serving'),
        CheckConstraint('calories >= 0', name='positive_calories'),
        CheckConstraint('protein_g >= 0 AND carbs_g >= 0 AND fats_g >= 0', name='positive_macros'),
    )
