"""Recipe-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.schemas.food_schema import FoodResponse


class IngredientBase(BaseModel):
    """Base ingredient schema."""
    food_id: UUID
    quantity: float = Field(..., gt=0)
    unit: str


class IngredientCreate(IngredientBase):
    """Schema for creating ingredient."""
    pass


class IngredientResponse(BaseModel):
    """Schema for ingredient response."""
    id: UUID
    food: FoodResponse
    quantity: float
    unit: str
    display_order: int

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    """Base recipe schema."""
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    prep_time_minutes: Optional[int] = Field(None, ge=0)
    cook_time_minutes: Optional[int] = Field(None, ge=0)
    servings: int = Field(..., gt=0)


class RecipeCreate(RecipeBase):
    """Schema for creating recipe."""
    ingredients: List[IngredientCreate]


class RecipeUpdate(RecipeBase):
    """Schema for updating recipe."""
    ingredients: Optional[List[IngredientCreate]] = None


class NutritionSummary(BaseModel):
    """Nutrition summary for recipe."""
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float


class RecipeResponse(RecipeBase):
    """Schema for recipe response."""
    id: UUID
    user_id: UUID
    is_public: bool
    created_at: datetime
    updated_at: datetime
    ingredients: List[IngredientResponse] = []
    nutrition_total: Optional[NutritionSummary] = None
    nutrition_per_serving: Optional[NutritionSummary] = None

    class Config:
        from_attributes = True


class RecipeListResponse(BaseModel):
    """Schema for recipe list response."""
    results: List[RecipeResponse]
    total: int
    page: int
    limit: int
