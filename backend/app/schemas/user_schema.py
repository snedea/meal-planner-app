"""User-related Pydantic schemas."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user creation."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for user update."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    activity_level: Optional[str] = None


class UserGoalsUpdate(BaseModel):
    """Schema for updating user goals."""
    goal_type: Optional[str] = None
    daily_calorie_target: Optional[int] = Field(None, gt=0)
    protein_target_g: Optional[float] = Field(None, ge=0)
    carbs_target_g: Optional[float] = Field(None, ge=0)
    fats_target_g: Optional[float] = Field(None, ge=0)
    water_target_ml: Optional[int] = Field(None, gt=0)


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    goal_type: Optional[str] = None
    daily_calorie_target: Optional[int] = None
    protein_target_g: Optional[float] = None
    carbs_target_g: Optional[float] = None
    fats_target_g: Optional[float] = None
    water_target_ml: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
