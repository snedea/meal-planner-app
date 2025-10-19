"""Main v1 API router."""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, foods, recipes, meal_logs

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(foods.router)
api_router.include_router(recipes.router)
api_router.include_router(meal_logs.router)
