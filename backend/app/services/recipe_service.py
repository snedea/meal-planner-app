"""Recipe service for creating and managing recipes."""
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from app.models.recipe import Recipe, RecipeIngredient
from app.models.food import Food
from app.schemas.recipe_schema import RecipeCreate, RecipeUpdate, RecipeResponse, NutritionSummary
from app.utils.nutrition_calculator import NutritionCalculator


class RecipeService:
    """Service for recipe operations."""

    def __init__(self, db: Session):
        self.db = db
        self.nutrition_calc = NutritionCalculator()

    def create_recipe(self, recipe_data: RecipeCreate, user_id: str) -> Recipe:
        """
        Create a new recipe with ingredients.

        Args:
            recipe_data: Recipe creation data
            user_id: User ID creating the recipe

        Returns:
            Created recipe with calculated nutrition
        """
        # Create recipe
        recipe = Recipe(
            id=uuid.uuid4(),
            user_id=user_id,
            name=recipe_data.name,
            description=recipe_data.description,
            instructions=recipe_data.instructions,
            prep_time_minutes=recipe_data.prep_time_minutes,
            cook_time_minutes=recipe_data.cook_time_minutes,
            servings=recipe_data.servings,
        )

        self.db.add(recipe)
        self.db.flush()

        # Add ingredients
        for idx, ingredient_data in enumerate(recipe_data.ingredients):
            ingredient = RecipeIngredient(
                id=uuid.uuid4(),
                recipe_id=recipe.id,
                food_id=ingredient_data.food_id,
                quantity=ingredient_data.quantity,
                unit=ingredient_data.unit,
                display_order=idx
            )
            self.db.add(ingredient)

        self.db.commit()
        self.db.refresh(recipe)

        return recipe

    def calculate_recipe_nutrition(self, recipe_id: str) -> dict:
        """
        Calculate total and per-serving nutrition for a recipe.

        Args:
            recipe_id: Recipe ID

        Returns:
            Dictionary with total and per_serving nutrition
        """
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        total_nutrition = {
            'calories': 0.0,
            'protein_g': 0.0,
            'carbs_g': 0.0,
            'fats_g': 0.0
        }

        # Calculate nutrition from all ingredients
        for ingredient in recipe.ingredients:
            food = ingredient.food
            if food and food.nutrition:
                nutrition_info = {
                    'serving_size': float(food.nutrition.serving_size),
                    'serving_unit': food.nutrition.serving_unit,
                    'calories': float(food.nutrition.calories),
                    'protein_g': float(food.nutrition.protein_g),
                    'carbs_g': float(food.nutrition.carbs_g),
                    'fats_g': float(food.nutrition.fats_g),
                }

                ingredient_nutrition = self.nutrition_calc.calculate_for_quantity(
                    nutrition_info,
                    float(ingredient.quantity),
                    ingredient.unit
                )

                for key in total_nutrition.keys():
                    total_nutrition[key] += ingredient_nutrition.get(key, 0)

        # Calculate per serving
        per_serving = self.nutrition_calc.per_serving(total_nutrition, recipe.servings)

        return {
            'total': total_nutrition,
            'per_serving': per_serving
        }

    def get_recipe_by_id(self, recipe_id: str, user_id: Optional[str] = None) -> Recipe:
        """
        Get recipe by ID.

        Args:
            recipe_id: Recipe ID
            user_id: Optional user ID for permission check

        Returns:
            Recipe object

        Raises:
            HTTPException: If recipe not found or user doesn't have permission
        """
        recipe = self.db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        # Check permission (user owns recipe or recipe is public)
        if user_id and str(recipe.user_id) != user_id and not recipe.is_public:
            raise HTTPException(status_code=403, detail="Not authorized to access this recipe")

        return recipe

    def get_user_recipes(self, user_id: str, page: int = 1, limit: int = 20) -> List[Recipe]:
        """
        Get all recipes for a user.

        Args:
            user_id: User ID
            page: Page number
            limit: Items per page

        Returns:
            List of recipes
        """
        offset = (page - 1) * limit
        recipes = self.db.query(Recipe).filter(
            Recipe.user_id == user_id
        ).offset(offset).limit(limit).all()

        return recipes

    def delete_recipe(self, recipe_id: str, user_id: str) -> bool:
        """
        Delete a recipe.

        Args:
            recipe_id: Recipe ID
            user_id: User ID (must own the recipe)

        Returns:
            True if deleted

        Raises:
            HTTPException: If recipe not found or user doesn't own it
        """
        recipe = self.get_recipe_by_id(recipe_id, user_id)

        if str(recipe.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this recipe")

        self.db.delete(recipe)
        self.db.commit()

        return True
