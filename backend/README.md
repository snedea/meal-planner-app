# Meal Planner Backend API

FastAPI-based backend for the Meal Planning and Nutrition Tracking application.

## Features

- **Authentication**: JWT-based authentication with bcrypt password hashing
- **Food Database**: Search foods with mocked external APIs (OpenFoodFacts/USDA)
- **Recipes**: Create recipes with automatic nutrition calculation
- **Meal Logging**: Track daily meals with nutrition summaries
- **Caching**: Redis caching for improved performance

## Tech Stack

- FastAPI 0.104+
- PostgreSQL 14+ (database)
- Redis 7+ (caching)
- SQLAlchemy 2.0 (ORM)
- Alembic (migrations)
- Pydantic v2 (validation)
- pytest (testing)

## Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (recommended)

### 2. Start Database Services

```bash
# Start PostgreSQL and Redis with Docker Compose
docker-compose up -d
```

### 3. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run Database Migrations

```bash
alembic upgrade head
```

### 6. Run the Application

```bash
# Development mode with auto-reload
python app/main.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

API Documentation: http://localhost:8000/docs

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens

### Users
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update user profile
- `PATCH /api/v1/users/me/goals` - Update nutrition goals

### Foods
- `GET /api/v1/foods/search?q={query}` - Search foods
- `GET /api/v1/foods/{id}` - Get food details
- `POST /api/v1/foods` - Create custom food

### Recipes
- `GET /api/v1/recipes` - Get user recipes
- `POST /api/v1/recipes` - Create recipe
- `GET /api/v1/recipes/{id}` - Get recipe details
- `DELETE /api/v1/recipes/{id}` - Delete recipe

### Meal Logs
- `GET /api/v1/meal-logs?date={YYYY-MM-DD}` - Get daily logs with summary
- `POST /api/v1/meal-logs` - Log a meal
- `DELETE /api/v1/meal-logs/{id}` - Delete meal log

## Project Structure

```
backend/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── api/v1/          # API endpoints
│   ├── services/        # Business logic
│   ├── utils/           # Utilities (auth, cache, etc.)
│   ├── config.py        # Settings
│   ├── database.py      # Database connection
│   └── main.py          # FastAPI app
├── alembic/             # Database migrations
├── tests/               # Unit and integration tests
├── requirements.txt     # Python dependencies
└── README.md
```

## Development

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### Code Quality

```bash
# Format code with black
black app/

# Lint with flake8
flake8 app/

# Type checking with mypy
mypy app/
```

## Notes

- External APIs (OpenFoodFacts, USDA) are mocked for MVP demo
- Replace mocked data in `external_api_service.py` with real API calls for production
- JWT tokens expire after 15 minutes (access) / 7 days (refresh)
- All passwords are hashed with bcrypt
