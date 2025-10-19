"""Meal log service for logging and tracking meals."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime
import uuid
from fastapi import HTTPException, status
from app.models.meal_log import MealLog
from app.models.user import User
from app.schemas.meal_log_schema import MealLogCreate, DailySummary
from app.utils.nutrition_calculator import NutritionCalculator


class MealLogService:
    """Service for meal log operations."""

    def __init__(self, db: Session):
        self.db = db
        self.nutrition_calc = NutritionCalculator()

    def create_meal_log(self, log_data: MealLogCreate, user_id: str) -> MealLog:
        """
        Create a meal log entry.

        Args:
            log_data: Meal log data
            user_id: User ID

        Returns:
            Created meal log with calculated nutrition
        """
        # Validate that either food_id or recipe_id is provided
        if not log_data.food_id and not log_data.recipe_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either food_id or recipe_id must be provided"
            )

        if log_data.food_id and log_data.recipe_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot log both food and recipe in the same entry"
            )

        # Calculate nutrition based on food or recipe
        nutrition = self._calculate_log_nutrition(log_data)

        # Create meal log
        meal_log = MealLog(
            id=uuid.uuid4(),
            user_id=user_id,
            food_id=log_data.food_id,
            recipe_id=log_data.recipe_id,
            quantity=log_data.quantity,
            unit=log_data.unit,
            meal_type=log_data.meal_type,
            logged_date=log_data.logged_date,
            logged_time=log_data.logged_time,
            notes=log_data.notes,
            calories=nutrition['calories'],
            protein_g=nutrition['protein_g'],
            carbs_g=nutrition['carbs_g'],
            fats_g=nutrition['fats_g'],
        )

        self.db.add(meal_log)
        self.db.commit()
        self.db.refresh(meal_log)

        return meal_log

    def _calculate_log_nutrition(self, log_data: MealLogCreate) -> dict:
        """
        Calculate nutrition for a meal log entry.

        Args:
            log_data: Meal log data

        Returns:
            Dictionary with nutrition values
        """
        from app.models.food import Food
        from app.models.recipe import Recipe

        if log_data.food_id:
            # Get food and calculate nutrition
            food = self.db.query(Food).filter(Food.id == log_data.food_id).first()
            if not food or not food.nutrition:
                raise HTTPException(status_code=404, detail="Food not found")

            nutrition_info = {
                'serving_size': float(food.nutrition.serving_size),
                'serving_unit': food.nutrition.serving_unit,
                'calories': float(food.nutrition.calories),
                'protein_g': float(food.nutrition.protein_g),
                'carbs_g': float(food.nutrition.carbs_g),
                'fats_g': float(food.nutrition.fats_g),
            }

            return self.nutrition_calc.calculate_for_quantity(
                nutrition_info,
                float(log_data.quantity),
                log_data.unit
            )

        elif log_data.recipe_id:
            # Get recipe and calculate nutrition
            from app.services.recipe_service import RecipeService
            recipe_service = RecipeService(self.db)
            nutrition = recipe_service.calculate_recipe_nutrition(str(log_data.recipe_id))

            # If logging servings of a recipe
            per_serving = nutrition['per_serving']
            multiplier = float(log_data.quantity)  # quantity = number of servings

            return {
                'calories': per_serving['calories'] * multiplier,
                'protein_g': per_serving['protein_g'] * multiplier,
                'carbs_g': per_serving['carbs_g'] * multiplier,
                'fats_g': per_serving['fats_g'] * multiplier,
            }

        return {'calories': 0, 'protein_g': 0, 'carbs_g': 0, 'fats_g': 0}

    def get_daily_logs(self, user_id: str, log_date: date) -> List[MealLog]:
        """
        Get all meal logs for a specific date.

        Args:
            user_id: User ID
            log_date: Date to get logs for

        Returns:
            List of meal logs
        """
        logs = self.db.query(MealLog).filter(
            MealLog.user_id == user_id,
            MealLog.logged_date == log_date
        ).order_by(MealLog.logged_time).all()

        return logs

    def calculate_daily_summary(self, user_id: str, log_date: date) -> DailySummary:
        """
        Calculate daily nutrition summary.

        Args:
            user_id: User ID
            log_date: Date to summarize

        Returns:
            Daily summary with totals and targets
        """
        # Get all logs for the day
        logs = self.get_daily_logs(user_id, log_date)

        # Calculate totals
        total_calories = sum(float(log.calories or 0) for log in logs)
        total_protein = sum(float(log.protein_g or 0) for log in logs)
        total_carbs = sum(float(log.carbs_g or 0) for log in logs)
        total_fats = sum(float(log.fats_g or 0) for log in logs)

        # Get user targets
        user = self.db.query(User).filter(User.id == user_id).first()

        summary = DailySummary(
            total_calories=total_calories,
            total_protein_g=total_protein,
            total_carbs_g=total_carbs,
            total_fats_g=total_fats,
            calorie_target=user.daily_calorie_target if user else None,
            protein_target_g=float(user.protein_target_g) if user and user.protein_target_g else None,
            carbs_target_g=float(user.carbs_target_g) if user and user.carbs_target_g else None,
            fats_target_g=float(user.fats_target_g) if user and user.fats_target_g else None,
        )

        # Calculate remaining
        if summary.calorie_target:
            summary.calorie_remaining = summary.calorie_target - total_calories
        if summary.protein_target_g:
            summary.protein_remaining_g = summary.protein_target_g - total_protein
        if summary.carbs_target_g:
            summary.carbs_remaining_g = summary.carbs_target_g - total_carbs
        if summary.fats_target_g:
            summary.fats_remaining_g = summary.fats_target_g - total_fats

        return summary

    def delete_meal_log(self, log_id: str, user_id: str) -> bool:
        """
        Delete a meal log.

        Args:
            log_id: Meal log ID
            user_id: User ID (must own the log)

        Returns:
            True if deleted

        Raises:
            HTTPException: If log not found or user doesn't own it
        """
        meal_log = self.db.query(MealLog).filter(MealLog.id == log_id).first()
        if not meal_log:
            raise HTTPException(status_code=404, detail="Meal log not found")

        if str(meal_log.user_id) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this log")

        self.db.delete(meal_log)
        self.db.commit()

        return True
