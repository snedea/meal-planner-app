# Installation Guide - Meal Planner MVP

This guide provides detailed step-by-step instructions for installing and running the Meal Planning and Nutrition Tracking application.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Installation](#detailed-installation)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [Running the Application](#running-the-application)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

1. **Docker and Docker Compose**
   - Docker Desktop 4.0+ (includes Docker Compose)
   - [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

2. **Python 3.11+**
   - Check version: `python3 --version`
   - [Download Python](https://www.python.org/downloads/)

3. **Node.js 18+** (for frontend - when implemented)
   - Check version: `node --version`
   - [Download Node.js](https://nodejs.org/)

4. **Git**
   - Check version: `git --version`
   - [Download Git](https://git-scm.com/downloads/)

### System Requirements

- **OS:** macOS, Linux, or Windows with WSL2
- **RAM:** 4GB minimum, 8GB recommended
- **Disk Space:** 2GB free space

---

## Quick Start

For experienced developers who want to get running quickly:

```bash
# Clone repository
git clone https://github.com/snedea/meal-planner-app.git
cd meal-planner-app

# Start databases
docker-compose up -d

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python app/main.py

# Access API
open http://localhost:8000/docs
```

---

## Detailed Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/snedea/meal-planner-app.git
cd meal-planner-app
```

### Step 2: Start Database Services

The application uses PostgreSQL and Redis, which run in Docker containers.

```bash
# Start containers in detached mode
docker-compose up -d

# Verify containers are running
docker-compose ps
```

Expected output:
```
NAME                 SERVICE      STATUS        PORTS
mealplanner_db       postgres     running       0.0.0.0:5432->5432/tcp
mealplanner_redis    redis        running       0.0.0.0:6379->6379/tcp
```

### Step 3: Backend Installation

#### Create Virtual Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

#### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI and Uvicorn (web framework)
- SQLAlchemy and Alembic (database)
- PostgreSQL driver (psycopg2)
- Redis client
- Authentication libraries (JWT, bcrypt)
- Testing tools (pytest)

#### Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env  # or vim, code, etc.
```

Default values should work for local development. See [Environment Configuration](#environment-configuration) for details.

#### Run Database Migrations

```bash
# Apply database migrations
alembic upgrade head
```

This creates all necessary tables in PostgreSQL.

### Step 4: Frontend Installation (Optional - Not Fully Implemented)

```bash
cd ../frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit if needed
nano .env
```

**Note:** Frontend components are not yet fully implemented (40% complete). Backend API is fully functional.

---

## Environment Configuration

### Backend Environment Variables

Edit `backend/.env`:

```env
# Application
APP_NAME=Meal Planner API
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
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

# CORS (add frontend URL when available)
CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# Server
HOST=0.0.0.0
PORT=8000
```

### Important Configuration Notes

**For Development:**
- Keep `DEBUG=True`
- Use default `DATABASE_URL`
- Use `DEMO_KEY` for USDA API (limited requests)

**For Production:**
- Set `DEBUG=False`
- Generate new `SECRET_KEY` (use: `openssl rand -hex 32`)
- Use strong database password
- Get real USDA API key (free at fdc.nal.usda.gov)
- Set `CORS_ORIGINS` to your frontend domain
- Use environment-specific DATABASE_URL

### Frontend Environment Variables

Edit `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## Database Setup

### Option 1: Docker Compose (Recommended)

```bash
# From project root
docker-compose up -d
```

This automatically:
- Creates PostgreSQL database
- Creates Redis instance
- Sets up volumes for data persistence
- Configures networking

### Option 2: Manual PostgreSQL Installation

If you prefer not to use Docker:

**Install PostgreSQL:**
- macOS: `brew install postgresql`
- Ubuntu: `sudo apt-get install postgresql`
- Windows: Download from postgresql.org

**Create Database:**
```bash
psql -U postgres
CREATE DATABASE mealplanner_db;
CREATE USER mealplanner WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE mealplanner_db TO mealplanner;
\q
```

**Update .env:**
```env
DATABASE_URL=postgresql://mealplanner:password@localhost:5432/mealplanner_db
```

### Database Migrations

```bash
cd backend
source venv/bin/activate

# View migration history
alembic history

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Create new migration (if you modify models)
alembic revision --autogenerate -m "description"
```

---

## Running the Application

### Start Backend Server

```bash
cd backend
source venv/bin/activate  # If not already activated
python app/main.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Access Points:**
- API Base: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- API Docs (ReDoc): http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Start Frontend (When Implemented)

```bash
cd frontend
npm run dev
```

Frontend will run at: http://localhost:5173

---

## Verification

### 1. Check Services are Running

```bash
# Check Docker containers
docker-compose ps

# Check backend is responding
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

### 2. Access API Documentation

Open browser: http://localhost:8000/docs

You should see the interactive Swagger UI with all endpoints.

### 3. Test User Registration

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

Expected: JSON response with user ID and email.

### 4. Test Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

Expected: JSON response with `access_token` and `refresh_token`.

---

## Troubleshooting

### Docker Issues

**Problem:** `Cannot connect to the Docker daemon`
```bash
# Solution: Start Docker Desktop
open -a Docker  # macOS
# Or search for Docker Desktop in applications
```

**Problem:** Port already in use (5432 or 6379)
```bash
# Find process using port
lsof -i :5432
# Kill process or change docker-compose.yml ports
```

### Database Connection Issues

**Problem:** `connection to server at "localhost" failed`
```bash
# Check PostgreSQL is running
docker-compose ps

# Check logs
docker-compose logs postgres

# Restart containers
docker-compose restart
```

### Python Virtual Environment Issues

**Problem:** `python3: command not found`
```bash
# Install Python 3
# macOS:
brew install python3

# Ubuntu:
sudo apt-get install python3 python3-pip python3-venv
```

**Problem:** `pip: command not found`
```bash
# Ensure pip is installed
python3 -m ensurepip --upgrade
```

### Alembic Migration Issues

**Problem:** `Can't locate revision identified by 'xyz'`
```bash
# Reset to base
alembic downgrade base

# Re-apply all migrations
alembic upgrade head
```

**Problem:** `Target database is not up to date`
```bash
# Check current revision
alembic current

# Check available revisions
alembic heads

# Upgrade to latest
alembic upgrade head
```

### Port Conflicts

If port 8000 is already in use:

Edit `backend/.env`:
```env
PORT=8001  # Or any available port
```

Then restart the backend server.

### Redis Connection Issues

**Problem:** `Error connecting to Redis`
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker exec -it mealplanner_redis redis-cli ping
# Expected: PONG

# Restart Redis
docker-compose restart redis
```

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`
```bash
# Ensure you're in backend directory
cd backend

# Set PYTHONPATH
export PYTHONPATH=/path/to/meal-planner-app/backend

# Or run with module syntax
python -m app.main
```

---

## Uninstallation

### Remove Application

```bash
cd meal-planner-app

# Stop containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Deactivate virtual environment
deactivate

# Remove project directory
cd ..
rm -rf meal-planner-app
```

### Remove Docker Images (Optional)

```bash
docker images | grep postgres
docker images | grep redis
docker rmi postgres:14-alpine redis:7-alpine
```

---

## Next Steps

After successful installation:

1. **Read the [Usage Guide](./USAGE.md)** to learn how to use the API
2. **Check [Architecture Documentation](./ARCHITECTURE.md)** to understand the system
3. **Review [API Documentation](http://localhost:8000/docs)** for endpoint details
4. **Run tests**: `cd backend && pytest`

---

## Getting Help

- **GitHub Issues:** https://github.com/snedea/meal-planner-app/issues
- **API Documentation:** http://localhost:8000/docs (when running)
- **Build Log:** See `.context-foundry/build-log.md` for implementation details

---

**Installation Guide Version:** 1.0
**Last Updated:** October 19, 2025
