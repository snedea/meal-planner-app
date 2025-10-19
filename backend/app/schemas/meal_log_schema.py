"""Meal log-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date, time
from uuid import UUID
from app.schemas.food_schema import FoodResponse
from app.schemas.recipe_schema import RecipeResponse


class MealLogBase(BaseModel):
    """Base meal log schema."""
    quantity: float = Field(..., gt=0)
    unit: str
    meal_type: str = Field(..., pattern='^(breakfast|lunch|dinner|snack)$')
    logged_date: date
    logged_time: Optional[time] = None
    notes: Optional[str] = None


class MealLogCreate(MealLogBase):
    """Schema for creating meal log."""
    food_id: Optional[UUID] = None
    recipe_id: Optional[UUID] = None

    class Config:
        # Ensure at least one of food_id or recipe_id is provided
        pass


class MealLogResponse(MealLogBase):
    """Schema for meal log response."""
    id: UUID
    user_id: UUID
    food: Optional[FoodResponse] = None
    recipe: Optional[RecipeResponse] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fats_g: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DailySummary(BaseModel):
    """Daily nutrition summary."""
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fats_g: float
    calorie_target: Optional[int] = None
    protein_target_g: Optional[float] = None
    carbs_target_g: Optional[float] = None
    fats_target_g: Optional[float] = None
    calorie_remaining: Optional[float] = None
    protein_remaining_g: Optional[float] = None
    carbs_remaining_g: Optional[float] = None
    fats_remaining_g: Optional[float] = None


class MealLogsResponse(BaseModel):
    """Response for meal logs with daily summary."""
    logs: List[MealLogResponse]
    summary: DailySummary


class DailySummaryItem(BaseModel):
    """Daily summary item for date range."""
    date: date
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fats_g: float
    meal_count: int


class SummaryRangeResponse(BaseModel):
    """Response for summary over date range."""
    daily_summaries: List[DailySummaryItem]
    averages: Dict[str, float]
