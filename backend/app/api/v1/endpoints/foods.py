"""Food endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.food_schema import FoodResponse, FoodCreate, FoodSearchResponse
from app.services.food_service import FoodService

router = APIRouter(prefix="/foods", tags=["foods"])


@router.get("/search", response_model=List[FoodResponse])
async def search_foods(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for foods.

    Args:
        q: Search query
        limit: Maximum number of results
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of matching foods
    """
    food_service = FoodService(db)
    results = await food_service.search_foods(q, limit)
    return results


@router.get("/{food_id}", response_model=FoodResponse)
def get_food(
    food_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get food by ID.

    Args:
        food_id: Food ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Food details
    """
    food_service = FoodService(db)
    food = food_service.get_food_by_id(food_id)
    return FoodResponse.model_validate(food)


@router.post("", response_model=FoodResponse, status_code=201)
def create_custom_food(
    food_data: FoodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create custom food.

    Args:
        food_data: Food creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created food
    """
    food_service = FoodService(db)
    food = food_service.create_custom_food(food_data, str(current_user.id))
    return FoodResponse.model_validate(food)
