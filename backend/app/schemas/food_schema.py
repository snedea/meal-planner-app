"""Food-related Pydantic schemas."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class NutritionInfoBase(BaseModel):
    """Base nutrition info schema."""
    serving_size: float = Field(..., gt=0)
    serving_unit: str
    servings_per_container: Optional[float] = None
    calories: float = Field(..., ge=0)
    protein_g: float = Field(default=0, ge=0)
    carbs_g: float = Field(default=0, ge=0)
    fats_g: float = Field(default=0, ge=0)
    fiber_g: Optional[float] = Field(None, ge=0)
    sugar_g: Optional[float] = Field(None, ge=0)
    saturated_fat_g: Optional[float] = Field(None, ge=0)
    trans_fat_g: Optional[float] = Field(None, ge=0)
    cholesterol_mg: Optional[float] = Field(None, ge=0)
    sodium_mg: Optional[float] = Field(None, ge=0)
    micronutrients: Optional[Dict[str, Any]] = None


class NutritionInfoCreate(NutritionInfoBase):
    """Schema for creating nutrition info."""
    pass


class NutritionInfoResponse(NutritionInfoBase):
    """Schema for nutrition info response."""
    id: UUID

    class Config:
        from_attributes = True


class FoodBase(BaseModel):
    """Base food schema."""
    name: str
    brand: Optional[str] = None
    description: Optional[str] = None


class FoodCreate(FoodBase):
    """Schema for creating custom food."""
    nutrition: NutritionInfoCreate


class FoodResponse(FoodBase):
    """Schema for food response."""
    id: UUID
    barcode: Optional[str] = None
    source: str
    source_id: Optional[str] = None
    is_verified: bool
    created_at: datetime
    nutrition: Optional[NutritionInfoResponse] = None

    class Config:
        from_attributes = True


class FoodSearchResponse(BaseModel):
    """Schema for food search response."""
    results: list[FoodResponse]
    total: int
    page: int
    limit: int
