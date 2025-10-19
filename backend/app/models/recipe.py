"""Recipe models."""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Recipe(Base):
    """Recipe model for user-created recipes."""

    __tablename__ = "recipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

    # Recipe details
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    instructions = Column(Text)

    # Timing
    prep_time_minutes = Column(Integer)
    cook_time_minutes = Column(Integer)

    # Servings
    servings = Column(Integer, nullable=False, default=1)

    # Visibility
    is_public = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    ingredients = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('servings > 0', name='positive_servings'),
    )


class RecipeIngredient(Base):
    """Junction table for recipe ingredients."""

    __tablename__ = "recipe_ingredients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recipe_id = Column(UUID(as_uuid=True), ForeignKey('recipes.id', ondelete='CASCADE'), nullable=False, index=True)
    food_id = Column(UUID(as_uuid=True), ForeignKey('foods.id', ondelete='RESTRICT'), nullable=False, index=True)

    # Quantity
    quantity = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=False)  # 'g', 'ml', 'cup', 'tbsp', etc.

    # Order in recipe
    display_order = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")
    food = relationship("Food")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='positive_quantity'),
    )
