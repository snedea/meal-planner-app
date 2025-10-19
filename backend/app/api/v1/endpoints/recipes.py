"""Recipe endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.recipe_schema import RecipeCreate, RecipeResponse, RecipeListResponse
from app.services.recipe_service import RecipeService

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("", response_model=List[RecipeResponse])
def get_recipes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's recipes.

    Args:
        page: Page number
        limit: Items per page
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of recipes
    """
    recipe_service = RecipeService(db)
    recipes = recipe_service.get_user_recipes(str(current_user.id), page, limit)

    # Calculate nutrition for each recipe
    results = []
    for recipe in recipes:
        nutrition = recipe_service.calculate_recipe_nutrition(str(recipe.id))
        recipe_response = RecipeResponse.model_validate(recipe)
        recipe_response.nutrition_total = nutrition['total']
        recipe_response.nutrition_per_serving = nutrition['per_serving']
        results.append(recipe_response)

    return results


@router.post("", response_model=RecipeResponse, status_code=201)
def create_recipe(
    recipe_data: RecipeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new recipe.

    Args:
        recipe_data: Recipe creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created recipe with nutrition
    """
    recipe_service = RecipeService(db)
    recipe = recipe_service.create_recipe(recipe_data, str(current_user.id))
    nutrition = recipe_service.calculate_recipe_nutrition(str(recipe.id))

    recipe_response = RecipeResponse.model_validate(recipe)
    recipe_response.nutrition_total = nutrition['total']
    recipe_response.nutrition_per_serving = nutrition['per_serving']

    return recipe_response


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get recipe by ID.

    Args:
        recipe_id: Recipe ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Recipe with nutrition
    """
    recipe_service = RecipeService(db)
    recipe = recipe_service.get_recipe_by_id(recipe_id, str(current_user.id))
    nutrition = recipe_service.calculate_recipe_nutrition(recipe_id)

    recipe_response = RecipeResponse.model_validate(recipe)
    recipe_response.nutrition_total = nutrition['total']
    recipe_response.nutrition_per_serving = nutrition['per_serving']

    return recipe_response


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a recipe.

    Args:
        recipe_id: Recipe ID
        current_user: Current authenticated user
        db: Database session
    """
    recipe_service = RecipeService(db)
    recipe_service.delete_recipe(recipe_id, str(current_user.id))
    return None
