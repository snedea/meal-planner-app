"""Food service for searching and managing foods."""
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from fastapi import HTTPException, status
from app.models.food import Food, NutritionInfo
from app.schemas.food_schema import FoodCreate, FoodResponse
from app.services.external_api_service import ExternalAPIService
from app.utils.cache import cache_get, cache_set


class FoodService:
    """Service for food operations."""

    def __init__(self, db: Session):
        self.db = db
        self.external_api = ExternalAPIService()

    async def search_foods(self, query: str, limit: int = 20) -> List[FoodResponse]:
        """
        Search for foods in local database and external APIs.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of food items
        """
        # 1. Check local database first
        local_results = self.db.query(Food).filter(
            Food.name.ilike(f"%{query}%")
        ).limit(limit).all()

        if len(local_results) >= 5:
            return [FoodResponse.model_validate(food) for food in local_results]

        # 2. Check Redis cache
        cache_key = f"food_search:{query}"
        cached_results = await cache_get(cache_key)
        if cached_results:
            return [FoodResponse(**result) for result in cached_results]

        # 3. Search external APIs
        external_results = await self.external_api.search_openfoodfacts(query, limit)

        # 4. Save external results to database
        saved_foods = []
        for result in external_results:
            food = self._save_external_food(result)
            if food:
                saved_foods.append(food)

        # 5. Combine and cache results
        all_foods = list(local_results) + saved_foods
        food_responses = [FoodResponse.model_validate(food) for food in all_foods[:limit]]

        # Cache for 1 hour
        await cache_set(
            cache_key,
            [food.model_dump() for food in food_responses],
            ttl=3600
        )

        return food_responses

    def _save_external_food(self, food_data: dict) -> Optional[Food]:
        """
        Save external food data to database.

        Args:
            food_data: External food data

        Returns:
            Saved food object or None if already exists
        """
        # Check if food already exists
        existing = self.db.query(Food).filter(
            Food.source == food_data["source"],
            Food.source_id == food_data["source_id"]
        ).first()

        if existing:
            return existing

        # Create food
        food = Food(
            id=uuid.uuid4(),
            name=food_data["name"],
            brand=food_data.get("brand"),
            source=food_data["source"],
            source_id=food_data["source_id"],
            description=food_data.get("description"),
            is_verified=True if food_data["source"] == "usda" else False
        )

        self.db.add(food)
        self.db.flush()

        # Create nutrition info
        nutrition_data = food_data["nutrition"]
        nutrition = NutritionInfo(
            id=uuid.uuid4(),
            food_id=food.id,
            serving_size=nutrition_data["serving_size"],
            serving_unit=nutrition_data["serving_unit"],
            calories=nutrition_data["calories"],
            protein_g=nutrition_data.get("protein_g", 0),
            carbs_g=nutrition_data.get("carbs_g", 0),
            fats_g=nutrition_data.get("fats_g", 0),
            fiber_g=nutrition_data.get("fiber_g"),
            sugar_g=nutrition_data.get("sugar_g"),
            saturated_fat_g=nutrition_data.get("saturated_fat_g"),
            trans_fat_g=nutrition_data.get("trans_fat_g"),
            cholesterol_mg=nutrition_data.get("cholesterol_mg"),
            sodium_mg=nutrition_data.get("sodium_mg"),
        )

        self.db.add(nutrition)
        self.db.commit()
        self.db.refresh(food)

        return food

    def get_food_by_id(self, food_id: str) -> Food:
        """
        Get food by ID.

        Args:
            food_id: Food ID

        Returns:
            Food object

        Raises:
            HTTPException: If food not found
        """
        food = self.db.query(Food).filter(Food.id == food_id).first()
        if not food:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food not found"
            )
        return food

    def create_custom_food(self, food_data: FoodCreate, user_id: str) -> Food:
        """
        Create custom food.

        Args:
            food_data: Food creation data
            user_id: User ID creating the food

        Returns:
            Created food object
        """
        # Create food
        food = Food(
            id=uuid.uuid4(),
            name=food_data.name,
            brand=food_data.brand,
            description=food_data.description,
            source="custom",
            created_by_user_id=user_id,
            is_verified=False
        )

        self.db.add(food)
        self.db.flush()

        # Create nutrition info
        nutrition_data = food_data.nutrition
        nutrition = NutritionInfo(
            id=uuid.uuid4(),
            food_id=food.id,
            serving_size=nutrition_data.serving_size,
            serving_unit=nutrition_data.serving_unit,
            servings_per_container=nutrition_data.servings_per_container,
            calories=nutrition_data.calories,
            protein_g=nutrition_data.protein_g,
            carbs_g=nutrition_data.carbs_g,
            fats_g=nutrition_data.fats_g,
            fiber_g=nutrition_data.fiber_g,
            sugar_g=nutrition_data.sugar_g,
            saturated_fat_g=nutrition_data.saturated_fat_g,
            trans_fat_g=nutrition_data.trans_fat_g,
            cholesterol_mg=nutrition_data.cholesterol_mg,
            sodium_mg=nutrition_data.sodium_mg,
            micronutrients=nutrition_data.micronutrients,
        )

        self.db.add(nutrition)
        self.db.commit()
        self.db.refresh(food)

        return food
