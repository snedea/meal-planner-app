"""External API service for food data (mocked for MVP)."""
from typing import List, Optional, Dict, Any
import uuid


class ExternalAPIService:
    """
    Service for external food APIs.
    For MVP, this uses mocked data instead of real API calls.
    """

    # Mock food database for demo purposes
    MOCK_FOODS = [
        {
            "name": "Chicken Breast, Raw",
            "brand": "Generic",
            "source": "usda",
            "source_id": "171077",
            "description": "Raw chicken breast without skin",
            "nutrition": {
                "serving_size": 100,
                "serving_unit": "g",
                "calories": 165,
                "protein_g": 31.0,
                "carbs_g": 0.0,
                "fats_g": 3.6,
                "saturated_fat_g": 1.0,
                "cholesterol_mg": 85,
                "sodium_mg": 74,
            }
        },
        {
            "name": "Brown Rice, Cooked",
            "brand": "Generic",
            "source": "usda",
            "source_id": "168878",
            "description": "Cooked brown rice",
            "nutrition": {
                "serving_size": 100,
                "serving_unit": "g",
                "calories": 112,
                "protein_g": 2.6,
                "carbs_g": 23.5,
                "fats_g": 0.9,
                "fiber_g": 1.8,
                "sodium_mg": 5,
            }
        },
        {
            "name": "Broccoli, Raw",
            "brand": None,
            "source": "usda",
            "source_id": "170379",
            "description": "Raw broccoli florets",
            "nutrition": {
                "serving_size": 100,
                "serving_unit": "g",
                "calories": 34,
                "protein_g": 2.8,
                "carbs_g": 6.6,
                "fats_g": 0.4,
                "fiber_g": 2.6,
                "sugar_g": 1.7,
                "sodium_mg": 33,
            }
        },
        {
            "name": "Salmon, Atlantic, Raw",
            "brand": "Generic",
            "source": "usda",
            "source_id": "175167",
            "description": "Raw Atlantic salmon",
            "nutrition": {
                "serving_size": 100,
                "serving_unit": "g",
                "calories": 208,
                "protein_g": 20.4,
                "carbs_g": 0.0,
                "fats_g": 13.4,
                "saturated_fat_g": 3.1,
                "cholesterol_mg": 55,
                "sodium_mg": 59,
            }
        },
        {
            "name": "Oatmeal, Dry",
            "brand": "Generic",
            "source": "usda",
            "source_id": "173904",
            "description": "Dry rolled oats",
            "nutrition": {
                "serving_size": 50,
                "serving_unit": "g",
                "calories": 190,
                "protein_g": 6.8,
                "carbs_g": 32.0,
                "fats_g": 3.4,
                "fiber_g": 5.0,
                "sugar_g": 1.0,
                "sodium_mg": 5,
            }
        },
        {
            "name": "Eggs, Whole, Raw",
            "brand": "Generic",
            "source": "usda",
            "source_id": "173424",
            "description": "Whole raw eggs",
            "nutrition": {
                "serving_size": 50,
                "serving_unit": "g",
                "calories": 72,
                "protein_g": 6.3,
                "carbs_g": 0.4,
                "fats_g": 4.8,
                "saturated_fat_g": 1.6,
                "cholesterol_mg": 186,
                "sodium_mg": 71,
            }
        },
        {
            "name": "Banana, Raw",
            "brand": None,
            "source": "usda",
            "source_id": "173944",
            "description": "Fresh banana",
            "nutrition": {
                "serving_size": 100,
                "serving_unit": "g",
                "calories": 89,
                "protein_g": 1.1,
                "carbs_g": 22.8,
                "fats_g": 0.3,
                "fiber_g": 2.6,
                "sugar_g": 12.2,
                "sodium_mg": 1,
            }
        },
        {
            "name": "Greek Yogurt, Plain, Nonfat",
            "brand": "Generic",
            "source": "usda",
            "source_id": "170903",
            "description": "Plain nonfat Greek yogurt",
            "nutrition": {
                "serving_size": 100,
                "serving_unit": "g",
                "calories": 59,
                "protein_g": 10.2,
                "carbs_g": 3.6,
                "fats_g": 0.4,
                "sugar_g": 3.2,
                "sodium_mg": 36,
            }
        },
    ]

    async def search_openfoodfacts(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search OpenFoodFacts API (mocked).

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of food items
        """
        # For MVP, return mocked data matching the query
        query_lower = query.lower()
        results = [
            food for food in self.MOCK_FOODS
            if query_lower in food["name"].lower()
        ]
        return results[:limit]

    async def search_usda(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search USDA API (mocked).

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of food items
        """
        # For MVP, return same mocked data
        return await self.search_openfoodfacts(query, limit)

    async def get_by_barcode_openfoodfacts(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Get food by barcode from OpenFoodFacts (mocked).

        Args:
            barcode: Product barcode

        Returns:
            Food data or None if not found
        """
        # For MVP, return None (barcode scanning not implemented)
        return None
