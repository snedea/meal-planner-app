# Architecture Document: Meal Planner MVP (Phase 1)

**Project:** Meal Planning & Nutrition Tracking Application
**Architect Phase Date:** October 19, 2025
**Scope:** Phase 1 MVP Only (Core Features)

---

## 1. SYSTEM ARCHITECTURE OVERVIEW

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT (Browser)                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │     React + TypeScript Application (Vite)           │   │
│  │  - Zustand State Management                         │   │
│  │  - React Router                                     │   │
│  │  - Recharts for Visualizations                     │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS/REST API
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI)                          │
│  ┌──────────────────────────────────────────────────┐      │
│  │         API Layer (Routes/Controllers)           │      │
│  └────────────────────┬─────────────────────────────┘      │
│                       ↓                                     │
│  ┌──────────────────────────────────────────────────┐      │
│  │       Service Layer (Business Logic)             │      │
│  │  - AuthService, FoodService, RecipeService      │      │
│  │  - ExternalAPIService (OpenFoodFacts, USDA)     │      │
│  └────────────────────┬─────────────────────────────┘      │
│                       ↓                                     │
│  ┌──────────────────────────────────────────────────┐      │
│  │      Repository Layer (Data Access)              │      │
│  │  - UserRepo, FoodRepo, RecipeRepo, MealLogRepo  │      │
│  └────────────────────┬─────────────────────────────┘      │
└────────────────────────┼─────────────────────────────────────┘
                        │
         ┌──────────────┴──────────────┐
         ↓                             ↓
┌────────────────────┐        ┌────────────────┐
│   PostgreSQL 14+   │        │    Redis 7+    │
│  (Primary Data)    │        │   (Caching)    │
└────────────────────┘        └────────────────┘
         ↑
         │ Cache Miss
         ↓
┌─────────────────────────────────────┐
│      External APIs                  │
│  - OpenFoodFacts API               │
│  - USDA FoodData Central API       │
└─────────────────────────────────────┘
```

### 1.2 Request Flow Example: Food Search

```
User types "chicken" in search
  ↓
React Component → Zustand Store → API Service
  ↓
FastAPI /api/v1/foods/search?q=chicken
  ↓
FoodService.search_foods()
  ↓
Check PostgreSQL foods table (local cache)
  ↓ (if not found)
Check Redis cache (key: "food_search:chicken")
  ↓ (if not found)
Call OpenFoodFacts API
  ↓ (if not found)
Call USDA API
  ↓
Store results in PostgreSQL + Redis
  ↓
Return JSON response to frontend
  ↓
Update Zustand store → Re-render component
```

---

## 2. DATABASE SCHEMA DESIGN

### 2.1 Schema Overview

**Tables for Phase 1:**
1. users - User accounts and profiles
2. foods - Master food database (local + external)
3. nutrition_info - Nutritional data per serving
4. recipes - User-created recipes
5. recipe_ingredients - Junction table
6. meal_logs - Daily food/recipe logging
7. favorites - User favorite foods/recipes
8. water_logs - Water intake tracking

### 2.2 Detailed Table Schemas

#### Table: users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),

    -- Profile data
    date_of_birth DATE,
    gender VARCHAR(20),  -- 'male', 'female', 'other', 'prefer_not_to_say'
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    activity_level VARCHAR(20), -- 'sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active'

    -- Goals
    goal_type VARCHAR(20), -- 'lose_weight', 'maintain_weight', 'gain_weight'
    daily_calorie_target INTEGER,
    protein_target_g DECIMAL(6,2),
    carbs_target_g DECIMAL(6,2),
    fats_target_g DECIMAL(6,2),
    water_target_ml INTEGER DEFAULT 2000,

    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_height CHECK (height_cm > 0),
    CONSTRAINT positive_weight CHECK (weight_kg > 0),
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### Table: foods

```sql
CREATE TABLE foods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    barcode VARCHAR(50),

    -- Source tracking
    source VARCHAR(20) NOT NULL, -- 'openfoodfacts', 'usda', 'custom'
    source_id VARCHAR(100), -- External API ID

    -- Metadata
    description TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    created_by_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_source CHECK (source IN ('openfoodfacts', 'usda', 'custom'))
);

CREATE INDEX idx_foods_name ON foods USING gin(to_tsvector('english', name));
CREATE INDEX idx_foods_barcode ON foods(barcode) WHERE barcode IS NOT NULL;
CREATE INDEX idx_foods_source_id ON foods(source, source_id);
CREATE INDEX idx_foods_created_by ON foods(created_by_user_id);
```

#### Table: nutrition_info

```sql
CREATE TABLE nutrition_info (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    food_id UUID NOT NULL REFERENCES foods(id) ON DELETE CASCADE,

    -- Serving information
    serving_size DECIMAL(10,2) NOT NULL,
    serving_unit VARCHAR(50) NOT NULL, -- 'g', 'ml', 'oz', 'cup', 'tbsp', 'piece', etc.
    servings_per_container DECIMAL(6,2),

    -- Macronutrients (per serving)
    calories DECIMAL(8,2) NOT NULL,
    protein_g DECIMAL(6,2) DEFAULT 0,
    carbs_g DECIMAL(6,2) DEFAULT 0,
    fats_g DECIMAL(6,2) DEFAULT 0,

    -- Additional macros
    fiber_g DECIMAL(6,2),
    sugar_g DECIMAL(6,2),
    saturated_fat_g DECIMAL(6,2),
    trans_fat_g DECIMAL(6,2),
    cholesterol_mg DECIMAL(6,2),
    sodium_mg DECIMAL(6,2),

    -- Micronutrients (JSONB for flexibility)
    micronutrients JSONB, -- {"vitamin_a_mcg": 100, "vitamin_c_mg": 50, ...}

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_serving CHECK (serving_size > 0),
    CONSTRAINT positive_calories CHECK (calories >= 0),
    CONSTRAINT positive_macros CHECK (protein_g >= 0 AND carbs_g >= 0 AND fats_g >= 0)
);

CREATE INDEX idx_nutrition_food ON nutrition_info(food_id);
```

#### Table: recipes

```sql
CREATE TABLE recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Recipe details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,

    -- Timing
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,

    -- Servings
    servings INTEGER NOT NULL DEFAULT 1,

    -- Visibility
    is_public BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_servings CHECK (servings > 0)
);

CREATE INDEX idx_recipes_user ON recipes(user_id);
CREATE INDEX idx_recipes_name ON recipes USING gin(to_tsvector('english', name));
CREATE INDEX idx_recipes_public ON recipes(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_recipes_created_at ON recipes(created_at DESC);
```

#### Table: recipe_ingredients

```sql
CREATE TABLE recipe_ingredients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id UUID NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    food_id UUID NOT NULL REFERENCES foods(id) ON DELETE RESTRICT,

    -- Quantity
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50) NOT NULL, -- 'g', 'ml', 'cup', 'tbsp', etc.

    -- Order in recipe
    display_order INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_quantity CHECK (quantity > 0),
    UNIQUE(recipe_id, food_id, display_order)
);

CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX idx_recipe_ingredients_food ON recipe_ingredients(food_id);
```

#### Table: meal_logs

```sql
CREATE TABLE meal_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- What was logged
    food_id UUID REFERENCES foods(id) ON DELETE SET NULL,
    recipe_id UUID REFERENCES recipes(id) ON DELETE SET NULL,

    -- Quantity consumed
    quantity DECIMAL(10,2) NOT NULL,
    unit VARCHAR(50) NOT NULL,

    -- Calculated nutrition (denormalized for performance)
    calories DECIMAL(8,2),
    protein_g DECIMAL(6,2),
    carbs_g DECIMAL(6,2),
    fats_g DECIMAL(6,2),

    -- When logged
    meal_type VARCHAR(20) NOT NULL, -- 'breakfast', 'lunch', 'dinner', 'snack'
    logged_date DATE NOT NULL,
    logged_time TIME,

    -- Notes
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_meal_type CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    CONSTRAINT has_food_or_recipe CHECK (
        (food_id IS NOT NULL AND recipe_id IS NULL) OR
        (food_id IS NULL AND recipe_id IS NOT NULL)
    ),
    CONSTRAINT positive_quantity CHECK (quantity > 0)
);

CREATE INDEX idx_meal_logs_user_date ON meal_logs(user_id, logged_date DESC);
CREATE INDEX idx_meal_logs_food ON meal_logs(food_id);
CREATE INDEX idx_meal_logs_recipe ON meal_logs(recipe_id);
CREATE INDEX idx_meal_logs_created_at ON meal_logs(created_at DESC);
```

#### Table: favorites

```sql
CREATE TABLE favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- What is favorited
    food_id UUID REFERENCES foods(id) ON DELETE CASCADE,
    recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT has_food_or_recipe CHECK (
        (food_id IS NOT NULL AND recipe_id IS NULL) OR
        (food_id IS NULL AND recipe_id IS NOT NULL)
    ),
    UNIQUE(user_id, food_id),
    UNIQUE(user_id, recipe_id)
);

CREATE INDEX idx_favorites_user ON favorites(user_id);
CREATE INDEX idx_favorites_food ON favorites(food_id);
CREATE INDEX idx_favorites_recipe ON favorites(recipe_id);
```

#### Table: water_logs

```sql
CREATE TABLE water_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Amount
    amount_ml INTEGER NOT NULL,

    -- When logged
    logged_date DATE NOT NULL,
    logged_time TIME,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT positive_amount CHECK (amount_ml > 0)
);

CREATE INDEX idx_water_logs_user_date ON water_logs(user_id, logged_date DESC);
```

---

## 3. BACKEND ARCHITECTURE

### 3.1 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Settings and environment variables
│   ├── database.py                # Database connection and session
│   │
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── food.py
│   │   ├── recipe.py
│   │   └── meal_log.py
│   │
│   ├── schemas/                   # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── food_schema.py
│   │   ├── recipe_schema.py
│   │   ├── meal_log_schema.py
│   │   └── auth_schema.py
│   │
│   ├── api/                       # API routes
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependency injection (get_db, get_current_user)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Main v1 router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py        # /auth/register, /auth/login, etc.
│   │           ├── users.py       # /users/me, /users/me/goals, etc.
│   │           ├── foods.py       # /foods/search, /foods/{id}, etc.
│   │           ├── recipes.py     # /recipes CRUD
│   │           └── meal_logs.py   # /meal-logs CRUD, /meal-logs/summary
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Authentication logic
│   │   ├── food_service.py        # Food search, external API integration
│   │   ├── recipe_service.py      # Recipe CRUD, nutrition calculation
│   │   ├── meal_log_service.py    # Meal logging, daily summary
│   │   └── external_api_service.py # OpenFoodFacts, USDA API calls
│   │
│   ├── repositories/              # Data access layer
│   │   ├── __init__.py
│   │   ├── base_repository.py     # Base CRUD operations
│   │   ├── user_repository.py
│   │   ├── food_repository.py
│   │   ├── recipe_repository.py
│   │   └── meal_log_repository.py
│   │
│   └── utils/                     # Utilities and helpers
│       ├── __init__.py
│       ├── auth.py                # JWT creation/validation, password hashing
│       ├── cache.py               # Redis caching utilities
│       ├── validators.py          # Custom validators
│       └── nutrition_calculator.py # Nutrition calculation helpers
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_auth.py
│   ├── test_foods.py
│   ├── test_recipes.py
│   ├── test_meal_logs.py
│   └── test_nutrition_calculator.py
│
├── alembic/                       # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── .env.example                   # Example environment variables
├── requirements.txt               # Python dependencies
├── pytest.ini                     # Pytest configuration
├── alembic.ini                    # Alembic configuration
└── README.md
```

### 3.2 API Endpoints Specification

#### Authentication Endpoints

**POST /api/v1/auth/register**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}

Response (201 Created):
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2025-10-19T10:00:00Z"
}
```

**POST /api/v1/auth/login**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}

Response (200 OK):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**POST /api/v1/auth/refresh**
```json
Request:
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response (200 OK):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

#### User Endpoints

**GET /api/v1/users/me**
```json
Headers: Authorization: Bearer <access_token>

Response (200 OK):
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "height_cm": 175.0,
  "weight_kg": 75.0,
  "activity_level": "moderately_active",
  "daily_calorie_target": 2000,
  "protein_target_g": 150.0,
  "carbs_target_g": 200.0,
  "fats_target_g": 65.0
}
```

**PATCH /api/v1/users/me**
```json
Headers: Authorization: Bearer <access_token>

Request:
{
  "height_cm": 180.0,
  "weight_kg": 80.0,
  "daily_calorie_target": 2200
}

Response (200 OK):
{
  "id": "uuid",
  "email": "user@example.com",
  ...updated fields...
}
```

#### Food Endpoints

**GET /api/v1/foods/search?q={query}&limit={limit}**
```json
Headers: Authorization: Bearer <access_token>

Response (200 OK):
{
  "results": [
    {
      "id": "uuid",
      "name": "Chicken Breast, Raw",
      "brand": "Generic",
      "source": "usda",
      "nutrition": {
        "serving_size": 100,
        "serving_unit": "g",
        "calories": 165,
        "protein_g": 31.0,
        "carbs_g": 0.0,
        "fats_g": 3.6
      }
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

**GET /api/v1/foods/{id}**
```json
Headers: Authorization: Bearer <access_token>

Response (200 OK):
{
  "id": "uuid",
  "name": "Chicken Breast, Raw",
  "brand": "Generic",
  "barcode": null,
  "source": "usda",
  "source_id": "171077",
  "nutrition": {
    "serving_size": 100,
    "serving_unit": "g",
    "calories": 165,
    "protein_g": 31.0,
    "carbs_g": 0.0,
    "fats_g": 3.6,
    "fiber_g": 0.0,
    "sodium_mg": 74
  }
}
```

**POST /api/v1/foods**
```json
Headers: Authorization: Bearer <access_token>

Request (Create custom food):
{
  "name": "My Homemade Protein Shake",
  "description": "Custom protein shake recipe",
  "nutrition": {
    "serving_size": 250,
    "serving_unit": "ml",
    "calories": 300,
    "protein_g": 35.0,
    "carbs_g": 20.0,
    "fats_g": 8.0
  }
}

Response (201 Created):
{
  "id": "uuid",
  "name": "My Homemade Protein Shake",
  "source": "custom",
  "created_by_user_id": "user-uuid",
  "nutrition": {...}
}
```

**GET /api/v1/foods/barcode/{barcode}**
```json
Headers: Authorization: Bearer <access_token>

Response (200 OK):
{
  "id": "uuid",
  "name": "Product Name",
  "barcode": "0123456789012",
  "nutrition": {...}
}

Response (404 Not Found):
{
  "detail": "Food not found for barcode: 0123456789012"
}
```

#### Recipe Endpoints

**GET /api/v1/recipes?page={page}&limit={limit}&search={query}**
```json
Headers: Authorization: Bearer <access_token>

Response (200 OK):
{
  "results": [
    {
      "id": "uuid",
      "name": "Grilled Chicken Salad",
      "servings": 2,
      "prep_time_minutes": 15,
      "cook_time_minutes": 10,
      "nutrition_per_serving": {
        "calories": 350,
        "protein_g": 40.0,
        "carbs_g": 15.0,
        "fats_g": 12.0
      }
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

**POST /api/v1/recipes**
```json
Headers: Authorization: Bearer <access_token>

Request:
{
  "name": "Grilled Chicken Salad",
  "description": "Healthy protein-packed salad",
  "instructions": "1. Grill chicken...\n2. Chop vegetables...",
  "servings": 2,
  "prep_time_minutes": 15,
  "cook_time_minutes": 10,
  "ingredients": [
    {
      "food_id": "chicken-breast-uuid",
      "quantity": 200,
      "unit": "g"
    },
    {
      "food_id": "lettuce-uuid",
      "quantity": 100,
      "unit": "g"
    }
  ]
}

Response (201 Created):
{
  "id": "uuid",
  "name": "Grilled Chicken Salad",
  "servings": 2,
  "ingredients": [...],
  "nutrition_per_serving": {
    "calories": 350,
    "protein_g": 40.0,
    "carbs_g": 15.0,
    "fats_g": 12.0
  }
}
```

**GET /api/v1/recipes/{id}**
```json
Headers: Authorization: Bearer <access_token>

Response (200 OK):
{
  "id": "uuid",
  "name": "Grilled Chicken Salad",
  "description": "...",
  "instructions": "...",
  "servings": 2,
  "ingredients": [
    {
      "food": {
        "id": "uuid",
        "name": "Chicken Breast",
        "nutrition": {...}
      },
      "quantity": 200,
      "unit": "g"
    }
  ],
  "nutrition_total": {...},
  "nutrition_per_serving": {...}
}
```

**PUT /api/v1/recipes/{id}**
```json
Headers: Authorization: Bearer <access_token>

Request: (same as POST)
Response (200 OK): (updated recipe)
```

**DELETE /api/v1/recipes/{id}**
```json
Headers: Authorization: Bearer <access_token>

Response (204 No Content)
```

#### Meal Log Endpoints

**GET /api/v1/meal-logs?date={YYYY-MM-DD}**
```json
Headers: Authorization: Bearer <access_token>

Response (200 OK):
{
  "logs": [
    {
      "id": "uuid",
      "meal_type": "breakfast",
      "food": {
        "id": "uuid",
        "name": "Oatmeal"
      },
      "quantity": 50,
      "unit": "g",
      "calories": 190,
      "protein_g": 6.8,
      "carbs_g": 32.0,
      "fats_g": 3.4,
      "logged_time": "08:30:00",
      "created_at": "2025-10-19T08:30:00Z"
    }
  ],
  "summary": {
    "total_calories": 1850,
    "total_protein_g": 125.0,
    "total_carbs_g": 180.0,
    "total_fats_g": 62.0,
    "calorie_target": 2000,
    "protein_target_g": 150.0,
    "carbs_target_g": 200.0,
    "fats_target_g": 65.0,
    "calorie_remaining": 150,
    "protein_remaining_g": 25.0,
    "carbs_remaining_g": 20.0,
    "fats_remaining_g": 3.0
  }
}
```

**POST /api/v1/meal-logs**
```json
Headers: Authorization: Bearer <access_token>

Request:
{
  "food_id": "uuid",  // OR "recipe_id": "uuid"
  "quantity": 150,
  "unit": "g",
  "meal_type": "lunch",
  "logged_date": "2025-10-19",
  "logged_time": "12:30:00",
  "notes": "Post-workout meal"
}

Response (201 Created):
{
  "id": "uuid",
  "meal_type": "lunch",
  "food": {...},
  "quantity": 150,
  "unit": "g",
  "calories": 250,
  "protein_g": 46.5,
  "carbs_g": 0.0,
  "fats_g": 5.4,
  "logged_date": "2025-10-19",
  "logged_time": "12:30:00"
}
```

**GET /api/v1/meal-logs/summary?start_date={date}&end_date={date}**
```json
Headers: Authorization: Bearer <access_token>

Response (200 OK):
{
  "daily_summaries": [
    {
      "date": "2025-10-19",
      "total_calories": 1850,
      "total_protein_g": 125.0,
      "total_carbs_g": 180.0,
      "total_fats_g": 62.0,
      "meal_count": 4
    },
    {
      "date": "2025-10-18",
      "total_calories": 2100,
      ...
    }
  ],
  "averages": {
    "avg_calories": 1975,
    "avg_protein_g": 130.0,
    "avg_carbs_g": 190.0,
    "avg_fats_g": 63.5
  }
}
```

**DELETE /api/v1/meal-logs/{id}**
```json
Headers: Authorization: Bearer <access_token>

Response (204 No Content)
```

### 3.3 Service Layer Design

**app/services/auth_service.py**
```python
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"sub": user_id, "exp": expire, "type": "access"}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def create_refresh_token(self, user_id: str) -> str:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {"sub": user_id, "exp": expire, "type": "refresh"}
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str) -> dict:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
```

**app/services/food_service.py**
```python
from app.repositories.food_repository import FoodRepository
from app.services.external_api_service import ExternalAPIService
from app.utils.cache import cache_get, cache_set

class FoodService:
    def __init__(self, food_repo: FoodRepository, external_api: ExternalAPIService):
        self.food_repo = food_repo
        self.external_api = external_api

    async def search_foods(self, query: str, limit: int = 20) -> list:
        # 1. Check local database
        local_results = await self.food_repo.search_by_name(query, limit)

        if len(local_results) >= 5:
            return local_results

        # 2. Check Redis cache
        cache_key = f"food_search:{query}"
        cached_results = await cache_get(cache_key)
        if cached_results:
            return cached_results

        # 3. Call external APIs
        external_results = []

        # Try OpenFoodFacts first
        off_results = await self.external_api.search_openfoodfacts(query, limit)
        external_results.extend(off_results)

        # If not enough, try USDA
        if len(external_results) < 5:
            usda_results = await self.external_api.search_usda(query, limit - len(external_results))
            external_results.extend(usda_results)

        # 4. Save to database and cache
        for result in external_results:
            await self.food_repo.create_from_external(result)

        combined_results = local_results + external_results
        await cache_set(cache_key, combined_results, ttl=3600)  # 1 hour

        return combined_results[:limit]

    async def get_by_barcode(self, barcode: str):
        # Check local database
        food = await self.food_repo.get_by_barcode(barcode)
        if food:
            return food

        # Try external APIs
        food_data = await self.external_api.get_by_barcode_openfoodfacts(barcode)
        if food_data:
            return await self.food_repo.create_from_external(food_data)

        return None
```

**app/services/recipe_service.py**
```python
from app.repositories.recipe_repository import RecipeRepository
from app.repositories.food_repository import FoodRepository
from app.utils.nutrition_calculator import NutritionCalculator

class RecipeService:
    def __init__(self, recipe_repo: RecipeRepository, food_repo: FoodRepository):
        self.recipe_repo = recipe_repo
        self.food_repo = food_repo
        self.nutrition_calc = NutritionCalculator()

    async def create_recipe(self, recipe_data: dict, user_id: str):
        # Create recipe
        recipe = await self.recipe_repo.create(recipe_data, user_id)

        # Add ingredients
        for ingredient in recipe_data['ingredients']:
            await self.recipe_repo.add_ingredient(
                recipe.id,
                ingredient['food_id'],
                ingredient['quantity'],
                ingredient['unit']
            )

        # Calculate nutrition
        nutrition = await self.calculate_recipe_nutrition(recipe.id)

        return {**recipe, 'nutrition_total': nutrition['total'], 'nutrition_per_serving': nutrition['per_serving']}

    async def calculate_recipe_nutrition(self, recipe_id: str):
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        ingredients = await self.recipe_repo.get_ingredients(recipe_id)

        total_nutrition = {
            'calories': 0,
            'protein_g': 0,
            'carbs_g': 0,
            'fats_g': 0
        }

        for ingredient in ingredients:
            food = await self.food_repo.get_by_id(ingredient.food_id)
            nutrition_for_quantity = self.nutrition_calc.calculate_for_quantity(
                food.nutrition,
                ingredient.quantity,
                ingredient.unit
            )

            for key in total_nutrition:
                total_nutrition[key] += nutrition_for_quantity.get(key, 0)

        per_serving_nutrition = {
            key: value / recipe.servings for key, value in total_nutrition.items()
        }

        return {
            'total': total_nutrition,
            'per_serving': per_serving_nutrition
        }
```

### 3.4 Caching Strategy

**Redis Cache Keys Structure:**
```
food_search:{query}              → TTL: 1 hour
food_barcode:{barcode}           → TTL: 24 hours
food_detail:{food_id}            → TTL: 24 hours
recipe_nutrition:{recipe_id}     → TTL: 1 hour (invalidate on update)
daily_summary:{user_id}:{date}   → TTL: 5 minutes
user_profile:{user_id}           → TTL: 15 minutes
```

**app/utils/cache.py**
```python
import redis.asyncio as redis
from app.config import settings
import json

redis_client = redis.from_url(settings.REDIS_URL)

async def cache_get(key: str):
    value = await redis_client.get(key)
    if value:
        return json.loads(value)
    return None

async def cache_set(key: str, value: any, ttl: int = 3600):
    await redis_client.setex(key, ttl, json.dumps(value))

async def cache_delete(key: str):
    await redis_client.delete(key)

async def cache_delete_pattern(pattern: str):
    keys = await redis_client.keys(pattern)
    if keys:
        await redis_client.delete(*keys)
```

---

## 4. FRONTEND ARCHITECTURE

### 4.1 Project Structure

```
frontend/
├── public/
│   └── vite.svg
│
├── src/
│   ├── main.tsx                   # Entry point
│   ├── App.tsx                    # Root component
│   ├── index.css                  # Global styles
│   │
│   ├── components/
│   │   ├── common/                # Reusable UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Spinner.tsx
│   │   │   └── Toast.tsx
│   │   │
│   │   ├── layout/                # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── MainLayout.tsx
│   │   │
│   │   ├── auth/                  # Authentication components
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   │
│   │   ├── food/                  # Food-related components
│   │   │   ├── FoodSearchBar.tsx
│   │   │   ├── FoodCard.tsx
│   │   │   ├── FoodDetailModal.tsx
│   │   │   ├── NutritionLabel.tsx
│   │   │   └── CreateFoodModal.tsx
│   │   │
│   │   ├── meal-log/              # Meal logging components
│   │   │   ├── MealLogForm.tsx
│   │   │   ├── MealLogList.tsx
│   │   │   ├── MealLogItem.tsx
│   │   │   ├── QuickAddButtons.tsx
│   │   │   └── DailyLogSummary.tsx
│   │   │
│   │   ├── recipe/                # Recipe components
│   │   │   ├── RecipeCard.tsx
│   │   │   ├── RecipeForm.tsx
│   │   │   ├── RecipeDetail.tsx
│   │   │   ├── IngredientsList.tsx
│   │   │   └── RecipeSearch.tsx
│   │   │
│   │   └── dashboard/             # Dashboard components
│   │       ├── CalorieProgress.tsx
│   │       ├── MacroBreakdown.tsx
│   │       ├── CalorieTrendChart.tsx
│   │       └── QuickActions.tsx
│   │
│   ├── pages/                     # Page components (routes)
│   │   ├── Landing.tsx            # Public landing page
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Dashboard.tsx          # Main dashboard
│   │   ├── FoodSearch.tsx
│   │   ├── MealLog.tsx
│   │   ├── Recipes.tsx
│   │   ├── RecipeDetail.tsx
│   │   └── Profile.tsx
│   │
│   ├── services/                  # API services
│   │   ├── api.ts                 # Axios instance with interceptors
│   │   ├── authService.ts
│   │   ├── foodService.ts
│   │   ├── recipeService.ts
│   │   └── mealLogService.ts
│   │
│   ├── store/                     # Zustand stores
│   │   ├── authStore.ts
│   │   ├── foodStore.ts
│   │   ├── mealLogStore.ts
│   │   ├── recipeStore.ts
│   │   └── uiStore.ts
│   │
│   ├── hooks/                     # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useFoodSearch.ts
│   │   ├── useMealLogs.ts
│   │   ├── useDebounce.ts
│   │   └── useToast.ts
│   │
│   ├── types/                     # TypeScript types
│   │   ├── user.types.ts
│   │   ├── food.types.ts
│   │   ├── recipe.types.ts
│   │   ├── mealLog.types.ts
│   │   └── api.types.ts
│   │
│   ├── utils/                     # Utility functions
│   │   ├── dateHelpers.ts
│   │   ├── nutritionCalculators.ts
│   │   ├── formatters.ts
│   │   └── validators.ts
│   │
│   └── config/                    # Configuration
│       └── constants.ts
│
├── tests/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── utils/
│
├── .env.example
├── .env.local
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

### 4.2 State Management (Zustand)

**src/store/authStore.ts**
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, LoginCredentials, RegisterData } from '../types/user.types';
import * as authService from '../services/authService';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authService.login(credentials);
          set({
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false
          });
          await get().fetchCurrentUser();
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null });
        try {
          await authService.register(data);
          // Auto-login after registration
          await get().login({ email: data.email, password: data.password });
        } catch (error: any) {
          set({ error: error.message, isLoading: false });
        }
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false });
      },

      refreshToken: async () => {
        // Implement token refresh logic
      },

      fetchCurrentUser: async () => {
        try {
          const user = await authService.getCurrentUser();
          set({ user });
        } catch (error) {
          set({ error: 'Failed to fetch user' });
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }) // Only persist token
    }
  )
);
```

**src/store/mealLogStore.ts**
```typescript
import { create } from 'zustand';
import { MealLog, CreateMealLog, DailySummary } from '../types/mealLog.types';
import * as mealLogService from '../services/mealLogService';

interface MealLogState {
  logs: MealLog[];
  currentDate: string; // YYYY-MM-DD
  dailySummary: DailySummary | null;
  isLoading: boolean;
  error: string | null;

  fetchLogs: (date: string) => Promise<void>;
  addLog: (log: CreateMealLog) => Promise<void>;
  updateLog: (id: string, log: Partial<CreateMealLog>) => Promise<void>;
  deleteLog: (id: string) => Promise<void>;
  setCurrentDate: (date: string) => void;
}

export const useMealLogStore = create<MealLogState>((set, get) => ({
  logs: [],
  currentDate: new Date().toISOString().split('T')[0],
  dailySummary: null,
  isLoading: false,
  error: null,

  fetchLogs: async (date) => {
    set({ isLoading: true, error: null });
    try {
      const data = await mealLogService.getMealLogs(date);
      set({
        logs: data.logs,
        dailySummary: data.summary,
        currentDate: date,
        isLoading: false
      });
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  addLog: async (log) => {
    set({ isLoading: true, error: null });
    try {
      const newLog = await mealLogService.createMealLog(log);
      set((state) => ({
        logs: [...state.logs, newLog],
        isLoading: false
      }));
      // Refresh daily summary
      await get().fetchLogs(get().currentDate);
    } catch (error: any) {
      set({ error: error.message, isLoading: false });
    }
  },

  deleteLog: async (id) => {
    try {
      await mealLogService.deleteMealLog(id);
      set((state) => ({
        logs: state.logs.filter((log) => log.id !== id)
      }));
      // Refresh daily summary
      await get().fetchLogs(get().currentDate);
    } catch (error: any) {
      set({ error: error.message });
    }
  },

  setCurrentDate: (date) => {
    set({ currentDate: date });
    get().fetchLogs(date);
  },

  updateLog: async (id, log) => {
    // Implementation
  }
}));
```

### 4.3 Routing Structure

**src/App.tsx**
```typescript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import FoodSearch from './pages/FoodSearch';
import MealLog from './pages/MealLog';
import Recipes from './pages/Recipes';
import RecipeDetail from './pages/RecipeDetail';
import Profile from './pages/Profile';
import MainLayout from './components/layout/MainLayout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<MainLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/food-search" element={<FoodSearch />} />
            <Route path="/meal-log" element={<MealLog />} />
            <Route path="/recipes" element={<Recipes />} />
            <Route path="/recipes/:id" element={<RecipeDetail />} />
            <Route path="/profile" element={<Profile />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

---

## 5. IMPLEMENTATION PLAN

### Step 1: Project Setup and Infrastructure (Estimated: 8 hours)

**Backend Setup:**
1. Initialize FastAPI project structure
2. Set up virtual environment and install dependencies
3. Configure PostgreSQL connection
4. Set up Alembic for migrations
5. Configure Redis connection
6. Create .env.example file
7. Set up pytest configuration

**Frontend Setup:**
1. Initialize Vite + React + TypeScript project
2. Install dependencies (Zustand, React Router, Recharts, Axios)
3. Set up Tailwind CSS or preferred CSS framework
4. Configure ESLint and Prettier
5. Set up Vitest for testing

**Docker Setup:**
1. Create docker-compose.yml for PostgreSQL + Redis
2. Create Dockerfile for backend (optional for local dev)
3. Create .dockerignore

**Deliverables:**
- Working development environment
- Database connection verified
- Redis connection verified
- Basic API responds to health check
- Frontend dev server running

### Step 2: Database Schema Creation (Estimated: 4 hours)

1. Create Alembic migration for all Phase 1 tables
2. Write migration with proper indexes and constraints
3. Run migration and verify schema
4. Seed development database with sample data
5. Create database fixtures for testing

**Deliverables:**
- All tables created in database
- Indexes and constraints in place
- Sample data loaded for development

### Step 3: Backend Models and Schemas (Estimated: 6 hours)

1. Create SQLAlchemy models for all tables
2. Create Pydantic schemas for request/response
3. Set up model relationships (Foreign Keys)
4. Create base repository with CRUD operations
5. Write unit tests for models

**Files to create:**
- app/models/*.py (all models)
- app/schemas/*.py (all schemas)
- app/repositories/base_repository.py
- tests/test_models.py

**Deliverables:**
- All ORM models defined
- All Pydantic schemas defined
- Basic CRUD operations working
- Model tests passing

### Step 4: Authentication System (Estimated: 10 hours)

1. Create JWT utility functions (create_token, verify_token)
2. Create password hashing utilities
3. Create AuthService with login/register logic
4. Create UserRepository
5. Create auth endpoints (register, login, refresh, me)
6. Create dependency for get_current_user
7. Write comprehensive auth tests

**Files to create:**
- app/utils/auth.py
- app/services/auth_service.py
- app/repositories/user_repository.py
- app/api/deps.py
- app/api/v1/endpoints/auth.py
- app/api/v1/endpoints/users.py
- tests/test_auth.py

**Testing:**
- Test user registration
- Test login with correct/incorrect credentials
- Test JWT token generation and validation
- Test protected endpoint access
- Test token refresh

**Deliverables:**
- Users can register
- Users can login and receive JWT
- Protected endpoints require valid JWT
- All auth tests passing

### Step 5: Food Database Integration (Estimated: 12 hours)

1. Create FoodRepository
2. Create ExternalAPIService (OpenFoodFacts + USDA clients)
3. Create FoodService with caching logic
4. Create food endpoints (search, get, create, barcode)
5. Implement Redis caching
6. Write API integration tests with mocked external APIs

**Files to create:**
- app/repositories/food_repository.py
- app/services/external_api_service.py
- app/services/food_service.py
- app/api/v1/endpoints/foods.py
- tests/test_foods.py
- tests/test_external_api.py

**Testing:**
- Test food search (local DB)
- Test food search (external APIs) with mocks
- Test barcode lookup
- Test custom food creation
- Test caching behavior

**Deliverables:**
- Food search working with external APIs
- Caching reducing API calls
- Custom foods can be created
- All food tests passing

### Step 6: Recipe System (Estimated: 10 hours)

1. Create RecipeRepository
2. Create RecipeService with nutrition calculation
3. Create NutritionCalculator utility
4. Create recipe endpoints (CRUD)
5. Write recipe tests

**Files to create:**
- app/repositories/recipe_repository.py
- app/services/recipe_service.py
- app/utils/nutrition_calculator.py
- app/api/v1/endpoints/recipes.py
- tests/test_recipes.py
- tests/test_nutrition_calculator.py

**Testing:**
- Test recipe creation with ingredients
- Test nutrition calculation accuracy
- Test recipe update and deletion
- Test recipe search

**Deliverables:**
- Recipes can be created with ingredients
- Nutrition is automatically calculated
- Recipes can be retrieved, updated, deleted
- All recipe tests passing

### Step 7: Meal Logging System (Estimated: 10 hours)

1. Create MealLogRepository
2. Create MealLogService with daily summary calculation
3. Create meal log endpoints (CRUD, summary)
4. Write meal log tests

**Files to create:**
- app/repositories/meal_log_repository.py
- app/services/meal_log_service.py
- app/api/v1/endpoints/meal_logs.py
- tests/test_meal_logs.py

**Testing:**
- Test meal log creation (food and recipe)
- Test daily summary calculation
- Test date range queries
- Test meal log deletion

**Deliverables:**
- Meals can be logged
- Daily summary accurately calculates totals
- Historical data can be queried
- All meal log tests passing

### Step 8: Backend API Documentation (Estimated: 2 hours)

1. Add OpenAPI metadata to FastAPI app
2. Add descriptions to all endpoints
3. Add example request/response to schemas
4. Verify Swagger UI at /docs

**Deliverables:**
- Complete API documentation at /docs
- All endpoints documented with examples

### Step 9: Frontend Foundation (Estimated: 8 hours)

1. Set up API client (Axios with interceptors)
2. Create Zustand stores (auth, food, mealLog, recipe, ui)
3. Create common components (Button, Input, Card, etc.)
4. Create layout components (Header, Sidebar, MainLayout)
5. Set up routing with React Router
6. Create ProtectedRoute component

**Files to create:**
- src/services/api.ts
- src/store/*.ts (all stores)
- src/components/common/*.tsx
- src/components/layout/*.tsx
- src/components/auth/ProtectedRoute.tsx
- src/App.tsx

**Deliverables:**
- API client configured with token interceptor
- State management working
- Basic layout rendering
- Routing configured

### Step 10: Authentication UI (Estimated: 8 hours)

1. Create Login page and form
2. Create Register page and form
3. Integrate with authStore
4. Add form validation
5. Add error handling and loading states
6. Create protected route logic
7. Add redirect after login

**Files to create:**
- src/pages/Login.tsx
- src/pages/Register.tsx
- src/components/auth/LoginForm.tsx
- src/components/auth/RegisterForm.tsx

**Testing:**
- Test form validation
- Test successful login
- Test failed login
- Test registration flow

**Deliverables:**
- Users can register via UI
- Users can login via UI
- JWT stored and used for API calls
- Protected routes redirect to login

### Step 11: Food Search UI (Estimated: 10 hours)

1. Create FoodSearch page
2. Create FoodSearchBar component with debounce
3. Create FoodCard component
4. Create FoodDetailModal with nutrition label
5. Create CreateFoodModal for custom foods
6. Integrate with foodStore
7. Add favorites functionality

**Files to create:**
- src/pages/FoodSearch.tsx
- src/components/food/FoodSearchBar.tsx
- src/components/food/FoodCard.tsx
- src/components/food/FoodDetailModal.tsx
- src/components/food/NutritionLabel.tsx
- src/components/food/CreateFoodModal.tsx
- src/hooks/useFoodSearch.ts
- src/hooks/useDebounce.ts

**Deliverables:**
- Users can search for foods
- Search results display clearly
- Food details show complete nutrition
- Custom foods can be created via modal

### Step 12: Meal Logging UI (Estimated: 12 hours)

1. Create MealLog page
2. Create MealLogForm component
3. Create MealLogList and MealLogItem components
4. Create QuickAddButtons for recent/favorites
5. Create DailyLogSummary component with progress bars
6. Integrate with mealLogStore
7. Add date navigation
8. Add edit/delete functionality

**Files to create:**
- src/pages/MealLog.tsx
- src/components/meal-log/MealLogForm.tsx
- src/components/meal-log/MealLogList.tsx
- src/components/meal-log/MealLogItem.tsx
- src/components/meal-log/QuickAddButtons.tsx
- src/components/meal-log/DailyLogSummary.tsx
- src/hooks/useMealLogs.ts

**Deliverables:**
- Users can log meals from food search
- Daily summary shows accurate totals and progress
- Users can navigate between dates
- Meals can be edited and deleted

### Step 13: Recipe UI (Estimated: 10 hours)

1. Create Recipes page (list view)
2. Create RecipeDetail page
3. Create RecipeForm component (create/edit)
4. Create RecipeCard component
5. Create IngredientsList component
6. Integrate with recipeStore
7. Add search and filtering

**Files to create:**
- src/pages/Recipes.tsx
- src/pages/RecipeDetail.tsx
- src/components/recipe/RecipeForm.tsx
- src/components/recipe/RecipeCard.tsx
- src/components/recipe/RecipeDetail.tsx
- src/components/recipe/IngredientsList.tsx

**Deliverables:**
- Users can view all recipes
- Users can create recipes with ingredients
- Nutrition is displayed per serving
- Recipes can be edited and deleted

### Step 14: Dashboard (Estimated: 12 hours)

1. Create Dashboard page
2. Create CalorieProgress component (circular or bar)
3. Create MacroBreakdown component (pie chart)
4. Create CalorieTrendChart component (line chart - 7 days)
5. Create QuickActions component
6. Integrate Recharts
7. Fetch and display today's summary

**Files to create:**
- src/pages/Dashboard.tsx
- src/components/dashboard/CalorieProgress.tsx
- src/components/dashboard/MacroBreakdown.tsx
- src/components/dashboard/CalorieTrendChart.tsx
- src/components/dashboard/QuickActions.tsx

**Deliverables:**
- Dashboard shows today's calorie/macro progress
- Charts visualize data clearly
- Quick actions provide shortcuts to common tasks
- Mobile responsive

### Step 15: Profile/Settings UI (Estimated: 6 hours)

1. Create Profile page
2. Create form to update user goals
3. Create form to update profile data
4. Integrate with authStore

**Files to create:**
- src/pages/Profile.tsx
- src/components/profile/ProfileForm.tsx
- src/components/profile/GoalsForm.tsx

**Deliverables:**
- Users can view their profile
- Users can update goals (calorie target, macros)
- Users can update personal data

### Step 16: Testing and QA (Estimated: 16 hours)

**Backend Testing:**
1. Achieve 85%+ test coverage
2. Write integration tests for all endpoints
3. Test error handling scenarios
4. Test caching behavior
5. Performance testing (response times)

**Frontend Testing:**
1. Write component tests for all major components
2. Test form validation
3. Test state management
4. Write E2E tests with Playwright:
   - User registration and login
   - Food search and logging
   - Recipe creation
   - Dashboard view

**Manual QA:**
1. Test on mobile devices (responsive design)
2. Test on different browsers
3. Test error scenarios (network failures, API errors)
4. Accessibility testing (keyboard navigation, screen readers)

**Deliverables:**
- 85%+ backend test coverage
- 80%+ frontend test coverage
- All E2E tests passing
- Mobile responsive verified
- Cross-browser compatibility verified

### Step 17: Documentation (Estimated: 4 hours)

1. Write backend README with setup instructions
2. Write frontend README with setup instructions
3. Create API documentation (if not auto-generated)
4. Create user guide (basic)
5. Document environment variables

**Deliverables:**
- Complete setup instructions
- API documentation
- User guide

### Step 18: Deployment Preparation (Estimated: 4 hours)

1. Set up production environment variables
2. Configure CORS for production
3. Set up database migrations for production
4. Create production Docker files (optional)
5. Set up CI/CD pipeline (GitHub Actions)

**Deliverables:**
- Production configuration ready
- CI/CD pipeline running tests
- Deployment guide created

---

## TOTAL ESTIMATED TIME: 142 hours (Phase 1 MVP)

**Timeline:**
- 1 developer: ~18 weeks (8 hours/week) or 4-5 weeks (full-time)
- 2 developers: ~9 weeks (8 hours/week) or 2-3 weeks (full-time)

---

## 6. TESTING REQUIREMENTS

### 6.1 Backend Testing Strategy

**Unit Tests (pytest):**

```python
# tests/test_nutrition_calculator.py
def test_calculate_for_quantity():
    nutrition = {
        'calories': 165,
        'protein_g': 31.0,
        'carbs_g': 0.0,
        'fats_g': 3.6,
        'serving_size': 100,
        'serving_unit': 'g'
    }

    result = NutritionCalculator().calculate_for_quantity(nutrition, 200, 'g')

    assert result['calories'] == 330
    assert result['protein_g'] == 62.0

# tests/test_auth.py
async def test_register_user_success(client):
    response = await client.post('/api/v1/auth/register', json={
        'email': 'test@example.com',
        'password': 'SecurePass123!',
        'first_name': 'Test'
    })
    assert response.status_code == 201
    assert 'id' in response.json()

async def test_login_success(client, test_user):
    response = await client.post('/api/v1/auth/login', json={
        'email': test_user.email,
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json()

# tests/test_foods.py
async def test_search_foods_local_db(client, auth_headers, sample_foods):
    response = await client.get('/api/v1/foods/search?q=chicken', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()['results']) > 0

async def test_search_foods_external_api(client, auth_headers, mock_openfoodfacts):
    response = await client.get('/api/v1/foods/search?q=newproduct', headers=auth_headers)
    assert response.status_code == 200
    # Verify external API was called and cached

# tests/test_recipes.py
async def test_create_recipe_calculates_nutrition(client, auth_headers, sample_foods):
    response = await client.post('/api/v1/recipes', headers=auth_headers, json={
        'name': 'Test Recipe',
        'servings': 2,
        'ingredients': [
            {'food_id': sample_foods[0].id, 'quantity': 100, 'unit': 'g'}
        ]
    })
    assert response.status_code == 201
    assert 'nutrition_per_serving' in response.json()
    assert response.json()['nutrition_per_serving']['calories'] > 0

# tests/test_meal_logs.py
async def test_create_meal_log(client, auth_headers, sample_food):
    response = await client.post('/api/v1/meal-logs', headers=auth_headers, json={
        'food_id': sample_food.id,
        'quantity': 150,
        'unit': 'g',
        'meal_type': 'lunch',
        'logged_date': '2025-10-19'
    })
    assert response.status_code == 201
    assert response.json()['calories'] > 0

async def test_daily_summary_calculation(client, auth_headers, sample_meal_logs):
    response = await client.get('/api/v1/meal-logs?date=2025-10-19', headers=auth_headers)
    assert response.status_code == 200
    summary = response.json()['summary']
    assert summary['total_calories'] > 0
    assert 'calorie_remaining' in summary
```

**Test Coverage Target:** 85%+

**How to run tests:**
```bash
cd backend
pytest --cov=app --cov-report=html
```

### 6.2 Frontend Testing Strategy

**Component Tests (Vitest + React Testing Library):**

```typescript
// tests/components/FoodSearchBar.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FoodSearchBar } from '../components/food/FoodSearchBar';

test('searches for food when user types', async () => {
  const onSearch = vi.fn();
  render(<FoodSearchBar onSearch={onSearch} />);

  const input = screen.getByPlaceholderText(/search for food/i);
  fireEvent.change(input, { target: { value: 'chicken' } });

  await waitFor(() => {
    expect(onSearch).toHaveBeenCalledWith('chicken');
  }, { timeout: 1000 }); // Debounce delay
});

// tests/pages/Dashboard.test.tsx
test('displays daily calorie progress', async () => {
  render(<Dashboard />);

  await waitFor(() => {
    expect(screen.getByText(/calories/i)).toBeInTheDocument();
    expect(screen.getByText(/1850/i)).toBeInTheDocument(); // Today's total
  });
});

// tests/services/authService.test.ts
test('login returns access token', async () => {
  const result = await authService.login({
    email: 'test@example.com',
    password: 'password'
  });

  expect(result.access_token).toBeDefined();
  expect(result.token_type).toBe('bearer');
});
```

**How to run tests:**
```bash
cd frontend
npm run test
npm run test:coverage
```

### 6.3 E2E Testing (Playwright)

```typescript
// tests/e2e/auth.spec.ts
test('user can register and login', async ({ page }) => {
  await page.goto('http://localhost:5173/register');

  await page.fill('input[name="email"]', 'newuser@example.com');
  await page.fill('input[name="password"]', 'SecurePass123!');
  await page.fill('input[name="first_name"]', 'Test');

  await page.click('button[type="submit"]');

  await expect(page).toHaveURL(/dashboard/);
});

// tests/e2e/meal-logging.spec.ts
test('user can search and log a meal', async ({ page }) => {
  // Login first
  await loginAsTestUser(page);

  // Navigate to meal log
  await page.goto('http://localhost:5173/meal-log');

  // Search for food
  await page.fill('input[placeholder*="search"]', 'chicken');
  await page.waitForSelector('text=Chicken Breast');

  // Select food
  await page.click('text=Chicken Breast');

  // Enter quantity
  await page.fill('input[name="quantity"]', '150');
  await page.selectOption('select[name="meal_type"]', 'lunch');

  // Submit
  await page.click('button:has-text("Log Meal")');

  // Verify meal appears in list
  await expect(page.locator('text=Chicken Breast')).toBeVisible();
});

// tests/e2e/recipe-creation.spec.ts
test('user can create recipe with nutrition calculation', async ({ page }) => {
  await loginAsTestUser(page);

  await page.goto('http://localhost:5173/recipes');
  await page.click('button:has-text("Create Recipe")');

  await page.fill('input[name="name"]', 'Test Recipe');
  await page.fill('input[name="servings"]', '2');

  // Add ingredient
  await page.click('button:has-text("Add Ingredient")');
  await page.fill('input[placeholder*="search ingredient"]', 'chicken');
  await page.click('text=Chicken Breast');
  await page.fill('input[name="ingredient_quantity"]', '200');

  await page.click('button[type="submit"]');

  // Verify nutrition was calculated
  await expect(page.locator('text=/calories/i')).toBeVisible();
});
```

**How to run E2E tests:**
```bash
cd frontend
npx playwright test
npx playwright test --ui  # Interactive mode
```

---

## 7. CONFIGURATION AND ENVIRONMENT

### 7.1 Backend Environment Variables

**backend/.env.example**
```env
# Application
APP_NAME=Meal Planner API
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://mealplanner:password@localhost:5432/mealplanner_db

# Redis
REDIS_URL=redis://localhost:6379/0

# External APIs
OPENFOODFACTS_API_URL=https://world.openfoodfacts.org/api/v2
USDA_API_KEY=DEMO_KEY
USDA_API_URL=https://api.nal.usda.gov/fdc/v1

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Server
HOST=0.0.0.0
PORT=8000
```

### 7.2 Frontend Environment Variables

**frontend/.env.example**
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 7.3 Docker Compose Setup

**docker-compose.yml**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    container_name: mealplanner_db
    environment:
      POSTGRES_USER: mealplanner
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mealplanner_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: mealplanner_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

---

## 8. SUCCESS CRITERIA

**MVP is considered "done" when:**

✅ **Functionality:**
- Users can register and login
- Users can search foods from external APIs
- Users can create custom foods
- Users can log meals (foods and recipes)
- Users can view daily nutrition summary
- Users can create recipes with automatic nutrition calculation
- Users can view calorie/macro progress on dashboard
- Users can update their goals and profile

✅ **Testing:**
- Backend test coverage ≥ 85%
- Frontend test coverage ≥ 80%
- All E2E tests passing
- Manual testing on mobile devices successful

✅ **Performance:**
- API response time < 200ms (95th percentile)
- Frontend initial load < 3 seconds
- Food search results appear within 1 second

✅ **Quality:**
- No critical bugs
- Error handling for all API failures
- Input validation on all forms
- Loading states for all async operations
- Mobile responsive design verified

✅ **Documentation:**
- API documentation available at /docs
- README with setup instructions
- Environment variables documented
- Basic user guide created

✅ **Security:**
- Passwords hashed with bcrypt
- JWT authentication working
- CORS configured properly
- No SQL injection vulnerabilities
- Input sanitization in place

---

## 9. PREVENTIVE MEASURES

### 9.1 API Rate Limiting
- Implement Redis-based caching for all external API calls
- Cache TTL: OpenFoodFacts (1 hour), USDA (24 hours)
- Database-first search strategy (check local before external)
- Rate limit monitoring (log API usage)

### 9.2 Database Performance
- Create indexes on all foreign keys
- Composite index on (user_id, date) for meal_logs
- Full-text search index on food names
- Regular EXPLAIN ANALYZE on slow queries

### 9.3 Security
- Password minimum requirements enforced (8+ chars, mixed case, numbers)
- JWT tokens with short expiration (15 min access, 7 day refresh)
- HTTPS only in production
- CORS restricted to frontend domain
- SQL injection prevention via ORM parameterized queries
- XSS prevention via React's built-in escaping
- Input validation with Pydantic

### 9.4 Error Handling
- Try-except blocks for all external API calls
- Graceful degradation (if OpenFoodFacts fails, try USDA)
- User-friendly error messages (no stack traces to client)
- Logging all errors for debugging
- Retry logic for transient failures

### 9.5 Data Validation
- Pydantic schemas for all API requests
- Check constraints in database (positive values, valid enums)
- Frontend form validation with clear error messages
- Nutritional data bounds checking (calories 0-5000, protein 0-300g)

---

## 10. KNOWN RISKS AND MITIGATIONS

### Risk 1: External API Downtime
**Impact:** High - Users cannot search for new foods
**Mitigation:**
- Fallback chain: OpenFoodFacts → USDA → Manual entry
- Aggressive caching (reduce dependency)
- Allow custom food creation as workaround
- Display clear message if APIs unavailable

### Risk 2: Slow Nutrition Calculation for Complex Recipes
**Impact:** Medium - Poor UX for recipe creation
**Mitigation:**
- Cache recipe nutrition (invalidate on update)
- Optimize queries with eager loading
- Limit ingredients per recipe (e.g., max 30)
- Background job for calculation if needed

### Risk 3: Database Growth (Meal Logs)
**Impact:** Low (Phase 1), High (Long-term)
**Mitigation:**
- Partition meal_logs table by month (future)
- Archive old data (>2 years)
- Pagination on all list endpoints
- Date range limits on queries

### Risk 4: Mobile Performance
**Impact:** Medium - Slow load times on mobile
**Mitigation:**
- Code splitting (lazy load routes)
- Optimize images
- Minimize bundle size
- Service worker for offline support (Phase 2)

### Risk 5: Data Quality from External APIs
**Impact:** Medium - Inaccurate nutrition data
**Mitigation:**
- Display data source to users
- Allow users to report incorrect data
- Prefer USDA (higher quality) where available
- Mark user-created foods differently

---

## CONCLUSION

This architecture provides a complete, production-ready blueprint for the Meal Planner MVP (Phase 1). The layered architecture ensures maintainability, the caching strategy addresses API rate limits, and the comprehensive testing plan ensures quality.

**Key Success Factors:**
1. Follow the implementation plan step-by-step
2. Write tests alongside features (not after)
3. Focus on Phase 1 scope only
4. Prioritize mobile responsiveness
5. Monitor API usage and optimize caching

**Next Step:** Begin implementation with Step 1 (Project Setup).

---

**Architect:** AUTONOMOUS ARCHITECT AGENT
**Architecture Completion Date:** October 19, 2025
**Ready for Builder Phase:** YES
