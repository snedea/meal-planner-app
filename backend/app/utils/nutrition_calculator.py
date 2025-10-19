"""Nutrition calculation utilities."""
from typing import Dict, Any


class NutritionCalculator:
    """Calculator for nutrition values based on quantity and serving size."""

    @staticmethod
    def calculate_for_quantity(
        nutrition_info: Dict[str, Any],
        quantity: float,
        unit: str
    ) -> Dict[str, float]:
        """
        Calculate nutrition values for a specific quantity.

        Args:
            nutrition_info: Nutrition information with serving_size and nutrients
            quantity: Quantity consumed
            unit: Unit of measurement

        Returns:
            Dictionary with calculated nutrition values
        """
        serving_size = float(nutrition_info.get('serving_size', 100))
        serving_unit = nutrition_info.get('serving_unit', 'g')

        # Convert quantity to serving size units if different
        # For MVP, we assume same units for simplicity
        # In production, implement unit conversion logic
        multiplier = quantity / serving_size

        result = {
            'calories': float(nutrition_info.get('calories', 0)) * multiplier,
            'protein_g': float(nutrition_info.get('protein_g', 0)) * multiplier,
            'carbs_g': float(nutrition_info.get('carbs_g', 0)) * multiplier,
            'fats_g': float(nutrition_info.get('fats_g', 0)) * multiplier,
        }

        # Include optional nutrients if present
        if 'fiber_g' in nutrition_info and nutrition_info['fiber_g']:
            result['fiber_g'] = float(nutrition_info['fiber_g']) * multiplier
        if 'sugar_g' in nutrition_info and nutrition_info['sugar_g']:
            result['sugar_g'] = float(nutrition_info['sugar_g']) * multiplier
        if 'sodium_mg' in nutrition_info and nutrition_info['sodium_mg']:
            result['sodium_mg'] = float(nutrition_info['sodium_mg']) * multiplier

        return result

    @staticmethod
    def sum_nutrition(nutrition_list: list[Dict[str, float]]) -> Dict[str, float]:
        """
        Sum nutrition values from multiple sources.

        Args:
            nutrition_list: List of nutrition dictionaries

        Returns:
            Dictionary with summed nutrition values
        """
        result = {
            'calories': 0.0,
            'protein_g': 0.0,
            'carbs_g': 0.0,
            'fats_g': 0.0,
        }

        for nutrition in nutrition_list:
            for key in result.keys():
                result[key] += nutrition.get(key, 0.0)

        return result

    @staticmethod
    def per_serving(
        total_nutrition: Dict[str, float],
        servings: int
    ) -> Dict[str, float]:
        """
        Calculate per-serving nutrition from total.

        Args:
            total_nutrition: Total nutrition values
            servings: Number of servings

        Returns:
            Per-serving nutrition values
        """
        if servings <= 0:
            servings = 1

        return {
            key: value / servings
            for key, value in total_nutrition.items()
        }
