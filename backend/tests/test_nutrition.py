"""Tests for nutrition calculation."""
from app.utils.nutrition_calculator import NutritionCalculator


def test_calculate_for_quantity():
    """Test nutrition calculation for specific quantity."""
    calc = NutritionCalculator()

    nutrition_info = {
        'serving_size': 100,
        'serving_unit': 'g',
        'calories': 165,
        'protein_g': 31.0,
        'carbs_g': 0.0,
        'fats_g': 3.6,
    }

    result = calc.calculate_for_quantity(nutrition_info, 200, 'g')

    assert result['calories'] == 330.0
    assert result['protein_g'] == 62.0
    assert result['carbs_g'] == 0.0
    assert result['fats_g'] == 7.2


def test_sum_nutrition():
    """Test summing nutrition from multiple sources."""
    calc = NutritionCalculator()

    nutrition_list = [
        {'calories': 100, 'protein_g': 10, 'carbs_g': 20, 'fats_g': 5},
        {'calories': 200, 'protein_g': 15, 'carbs_g': 25, 'fats_g': 8},
    ]

    result = calc.sum_nutrition(nutrition_list)

    assert result['calories'] == 300.0
    assert result['protein_g'] == 25.0
    assert result['carbs_g'] == 45.0
    assert result['fats_g'] == 13.0


def test_per_serving():
    """Test calculating per-serving nutrition."""
    calc = NutritionCalculator()

    total_nutrition = {
        'calories': 400,
        'protein_g': 40,
        'carbs_g': 60,
        'fats_g': 20,
    }

    result = calc.per_serving(total_nutrition, 2)

    assert result['calories'] == 200.0
    assert result['protein_g'] == 20.0
    assert result['carbs_g'] == 30.0
    assert result['fats_g'] == 10.0


def test_per_serving_single_serving():
    """Test per-serving calculation with 1 serving."""
    calc = NutritionCalculator()

    total_nutrition = {
        'calories': 300,
        'protein_g': 25,
        'carbs_g': 30,
        'fats_g': 12,
    }

    result = calc.per_serving(total_nutrition, 1)

    assert result == total_nutrition
