"""Meal log endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.meal_log_schema import MealLogCreate, MealLogResponse, MealLogsResponse
from app.services.meal_log_service import MealLogService

router = APIRouter(prefix="/meal-logs", tags=["meal-logs"])


@router.get("", response_model=MealLogsResponse)
def get_meal_logs(
    date: date = Query(..., description="Date to get logs for (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get meal logs for a specific date with daily summary.

    Args:
        date: Date to get logs for
        current_user: Current authenticated user
        db: Database session

    Returns:
        Meal logs and daily summary
    """
    meal_log_service = MealLogService(db)
    logs = meal_log_service.get_daily_logs(str(current_user.id), date)
    summary = meal_log_service.calculate_daily_summary(str(current_user.id), date)

    return MealLogsResponse(
        logs=[MealLogResponse.model_validate(log) for log in logs],
        summary=summary
    )


@router.post("", response_model=MealLogResponse, status_code=201)
def create_meal_log(
    log_data: MealLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a meal log entry.

    Args:
        log_data: Meal log data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created meal log
    """
    meal_log_service = MealLogService(db)
    meal_log = meal_log_service.create_meal_log(log_data, str(current_user.id))
    return MealLogResponse.model_validate(meal_log)


@router.delete("/{log_id}", status_code=204)
def delete_meal_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a meal log.

    Args:
        log_id: Meal log ID
        current_user: Current authenticated user
        db: Database session
    """
    meal_log_service = MealLogService(db)
    meal_log_service.delete_meal_log(log_id, str(current_user.id))
    return None
