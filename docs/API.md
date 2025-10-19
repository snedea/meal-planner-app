# API Documentation - Meal Planner MVP

Complete API reference for the Meal Planning and Nutrition Tracking application.

**Base URL:** `http://localhost:8000/api/v1`

**Interactive Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Table of Contents

1. [Authentication](#authentication)
2. [Users](#users)
3. [Foods](#foods)
4. [Recipes](#recipes)
5. [Meal Logs](#meal-logs)
6. [Error Responses](#error-responses)

---

## Authentication

All endpoints except `/auth/register` and `/auth/login` require authentication.

**Authentication Method:** Bearer Token (JWT)

**Header Format:**
```
Authorization: Bearer <access_token>
```

### POST /auth/register

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "created_at": "2025-10-19T10:00:00Z"
}
```

**Validation Rules:**
- Email must be valid format
- Password minimum 8 characters
- Email must be unique

### POST /auth/login

Login and receive JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Token Lifetimes:**
- Access Token: 15 minutes
- Refresh Token: 7 days

---

## Users

### GET /users/me

Get current authenticated user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": null,
  "gender": null,
  "height_cm": null,
  "weight_kg": null,
  "activity_level": null,
  "goal_type": null,
  "daily_calorie_target": 2000,
  "protein_target_g": 150.0,
  "carbs_target_g": 200.0,
  "fats_target_g": 65.0,
  "water_target_ml": 2000,
  "created_at": "2025-10-19T10:00:00Z",
  "updated_at": "2025-10-19T10:00:00Z"
}
```

### PATCH /users/me

Update current user's profile or goals.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request (Partial Update):**
```json
{
  "height_cm": 180.0,
  "weight_kg": 80.5,
  "daily_calorie_target": 2200,
  "protein_target_g": 165.0
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  ...updated fields...
}
```

**Updatable Fields:**
- Profile: first_name, last_name, date_of_birth, gender, height_cm, weight_kg, activity_level
- Goals: goal_type, daily_calorie_target, protein_target_g, carbs_target_g, fats_target_g, water_target_ml

---

## Foods

### GET /foods/search

Search for foods in the database and external APIs.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `q` (required): Search query string
- `limit` (optional): Maximum results (default: 20, max: 100)

**Example:**
```
GET /api/v1/foods/search?q=chicken&limit=10
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "food-uuid-1",
      "name": "Chicken Breast, Raw",
      "brand": null,
      "source": "usda",
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
  ],
  "total": 8,
  "page": 1,
  "limit": 10
}
```

**Search Strategy:**
1. Check local database
2. Check Redis cache
3. Query OpenFoodFacts API (mocked in MVP)
4. Query USDA API (mocked in MVP)
5. Cache results

### GET /foods/{id}

Get detailed information about a specific food.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "food-uuid-1",
  "name": "Chicken Breast, Raw",
  "brand": null,
  "barcode": null,
  "source": "usda",
  "source_id": "171077",
  "description": "Raw chicken breast meat",
  "nutrition": {
    "serving_size": 100,
    "serving_unit": "g",
    "calories": 165,
    "protein_g": 31.0,
    "carbs_g": 0.0,
    "fats_g": 3.6,
    "fiber_g": 0.0,
    "sugar_g": 0.0,
    "saturated_fat_g": 1.0,
    "sodium_mg": 74,
    "micronutrients": {}
  },
  "created_at": "2025-10-19T10:00:00Z"
}
```

### POST /foods

Create a custom food item.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "My Protein Shake",
  "description": "Custom protein shake recipe",
  "nutrition": {
    "serving_size": 250,
    "serving_unit": "ml",
    "calories": 300,
    "protein_g": 35.0,
    "carbs_g": 20.0,
    "fats_g": 8.0,
    "fiber_g": 2.0,
    "sugar_g": 10.0
  }
}
```

**Response (201 Created):**
```json
{
  "id": "food-uuid-new",
  "name": "My Protein Shake",
  "source": "custom",
  "created_by_user_id": "user-uuid",
  "nutrition": {...}
}
```

### GET /foods/barcode/{barcode}

Look up food by barcode.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Example:**
```
GET /api/v1/foods/barcode/0123456789012
```

**Response (200 OK):**
```json
{
  "id": "food-uuid",
  "name": "Product Name",
  "barcode": "0123456789012",
  "brand": "Brand Name",
  "nutrition": {...}
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Food not found for barcode: 0123456789012"
}
```

---

## Recipes

### GET /recipes

List all recipes for the current user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (default: 20, max: 100)
- `search` (optional): Filter by name

**Example:**
```
GET /api/v1/recipes?page=1&limit=10&search=chicken
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "recipe-uuid-1",
      "name": "Grilled Chicken Salad",
      "description": "Healthy protein-packed salad",
      "servings": 2,
      "prep_time_minutes": 15,
      "cook_time_minutes": 10,
      "is_public": false,
      "nutrition_per_serving": {
        "calories": 350,
        "protein_g": 40.0,
        "carbs_g": 15.0,
        "fats_g": 12.0
      },
      "created_at": "2025-10-19T10:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 10
}
```

### GET /recipes/{id}

Get detailed recipe information including ingredients.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "recipe-uuid-1",
  "name": "Grilled Chicken Salad",
  "description": "Healthy protein-packed salad",
  "instructions": "1. Grill chicken...\n2. Chop vegetables...",
  "servings": 2,
  "prep_time_minutes": 15,
  "cook_time_minutes": 10,
  "is_public": false,
  "ingredients": [
    {
      "food": {
        "id": "chicken-uuid",
        "name": "Chicken Breast",
        "nutrition": {...}
      },
      "quantity": 200,
      "unit": "g",
      "display_order": 1
    },
    {
      "food": {
        "id": "lettuce-uuid",
        "name": "Romaine Lettuce",
        "nutrition": {...}
      },
      "quantity": 100,
      "unit": "g",
      "display_order": 2
    }
  ],
  "nutrition_total": {
    "calories": 700,
    "protein_g": 80.0,
    "carbs_g": 30.0,
    "fats_g": 24.0
  },
  "nutrition_per_serving": {
    "calories": 350,
    "protein_g": 40.0,
    "carbs_g": 15.0,
    "fats_g": 12.0
  },
  "created_at": "2025-10-19T10:00:00Z"
}
```

### POST /recipes

Create a new recipe.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "name": "Grilled Chicken Salad",
  "description": "Healthy protein-packed salad",
  "instructions": "1. Grill chicken breast for 8-10 minutes\n2. Chop romaine lettuce\n3. Combine and serve",
  "servings": 2,
  "prep_time_minutes": 15,
  "cook_time_minutes": 10,
  "ingredients": [
    {
      "food_id": "chicken-uuid",
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
```

**Response (201 Created):**
```json
{
  "id": "recipe-uuid-new",
  "name": "Grilled Chicken Salad",
  "servings": 2,
  "ingredients": [...],
  "nutrition_total": {...},
  "nutrition_per_serving": {...}
}
```

**Validation:**
- Name required
- Servings must be > 0
- At least one ingredient required
- Food IDs must exist

### DELETE /recipes/{id}

Delete a recipe (user must be owner).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

## Meal Logs

### GET /meal-logs

Get meal logs for a specific date with daily summary.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `date` (optional): Date in YYYY-MM-DD format (default: today)

**Example:**
```
GET /api/v1/meal-logs?date=2025-10-19
```

**Response (200 OK):**
```json
{
  "logs": [
    {
      "id": "log-uuid-1",
      "meal_type": "breakfast",
      "food": {
        "id": "oatmeal-uuid",
        "name": "Oatmeal"
      },
      "recipe": null,
      "quantity": 50,
      "unit": "g",
      "calories": 190,
      "protein_g": 6.8,
      "carbs_g": 32.0,
      "fats_g": 3.4,
      "logged_date": "2025-10-19",
      "logged_time": "08:30:00",
      "notes": null,
      "created_at": "2025-10-19T08:30:00Z"
    },
    {
      "id": "log-uuid-2",
      "meal_type": "lunch",
      "food": null,
      "recipe": {
        "id": "recipe-uuid",
        "name": "Grilled Chicken Salad"
      },
      "quantity": 1,
      "unit": "serving",
      "calories": 350,
      "protein_g": 40.0,
      "carbs_g": 15.0,
      "fats_g": 12.0,
      "logged_date": "2025-10-19",
      "logged_time": "12:30:00",
      "notes": "Post-workout meal",
      "created_at": "2025-10-19T12:30:00Z"
    }
  ],
  "summary": {
    "date": "2025-10-19",
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
    "fats_remaining_g": 3.0,
    "calorie_progress_percent": 92.5,
    "protein_progress_percent": 83.3,
    "carbs_progress_percent": 90.0,
    "fats_progress_percent": 95.4
  }
}
```

### POST /meal-logs

Log a food or recipe to your daily diary.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request (Log Food):**
```json
{
  "food_id": "chicken-uuid",
  "quantity": 150,
  "unit": "g",
  "meal_type": "lunch",
  "logged_date": "2025-10-19",
  "logged_time": "12:30:00",
  "notes": "Post-workout meal"
}
```

**Request (Log Recipe):**
```json
{
  "recipe_id": "recipe-uuid",
  "quantity": 1,
  "unit": "serving",
  "meal_type": "dinner",
  "logged_date": "2025-10-19",
  "logged_time": "19:00:00"
}
```

**Response (201 Created):**
```json
{
  "id": "log-uuid-new",
  "meal_type": "lunch",
  "food": {...},
  "quantity": 150,
  "unit": "g",
  "calories": 248,
  "protein_g": 46.5,
  "carbs_g": 0.0,
  "fats_g": 5.4,
  "logged_date": "2025-10-19",
  "logged_time": "12:30:00",
  "notes": "Post-workout meal"
}
```

**Validation:**
- Must provide either food_id OR recipe_id (not both)
- Quantity must be > 0
- meal_type must be: breakfast, lunch, dinner, or snack
- logged_date must be valid date

### DELETE /meal-logs/{id}

Delete a meal log entry.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

### GET /meal-logs/summary

Get nutrition summary for a date range.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)

**Example:**
```
GET /api/v1/meal-logs/summary?start_date=2025-10-13&end_date=2025-10-19
```

**Response (200 OK):**
```json
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
      "total_protein_g": 145.0,
      "total_carbs_g": 210.0,
      "total_fats_g": 68.0,
      "meal_count": 5
    }
  ],
  "averages": {
    "avg_calories": 1975.0,
    "avg_protein_g": 135.0,
    "avg_carbs_g": 195.0,
    "avg_fats_g": 65.0
  }
}
```

---

## Error Responses

All error responses follow a consistent format:

### 400 Bad Request
```json
{
  "detail": "Validation error description"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently not implemented in MVP. Will be added in Phase 2.

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1, min: 1)
- `limit`: Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "results": [...],
  "total": 50,
  "page": 2,
  "limit": 20,
  "pages": 3
}
```

---

## Filtering and Sorting

### Search
Food and recipe endpoints support search:
```
GET /api/v1/foods/search?q=chicken
GET /api/v1/recipes?search=salad
```

### Sorting
Not yet implemented. Coming in Phase 2.

---

## Sample Workflow

### 1. Register and Login

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"SecurePass123!","first_name":"Demo"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"SecurePass123!"}'

# Save the access_token from response
TOKEN="your-access-token-here"
```

### 2. Set Goals

```bash
curl -X PATCH http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"daily_calorie_target":2200,"protein_target_g":165}'
```

### 3. Search for Foods

```bash
curl -X GET "http://localhost:8000/api/v1/foods/search?q=chicken" \
  -H "Authorization: Bearer $TOKEN"

# Save a food_id from results
FOOD_ID="food-uuid-here"
```

### 4. Log a Meal

```bash
curl -X POST http://localhost:8000/api/v1/meal-logs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"food_id\":\"$FOOD_ID\",
    \"quantity\":200,
    \"unit\":\"g\",
    \"meal_type\":\"lunch\",
    \"logged_date\":\"2025-10-19\"
  }"
```

### 5. View Daily Summary

```bash
curl -X GET "http://localhost:8000/api/v1/meal-logs?date=2025-10-19" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Interactive API Exploration

For the best API exploration experience, use the built-in Swagger UI:

1. Start the backend server
2. Open http://localhost:8000/docs
3. Click "Authorize" and enter your JWT token
4. Try out endpoints interactively

---

**API Documentation Version:** 1.0
**Last Updated:** October 19, 2025
**API Version:** v1
