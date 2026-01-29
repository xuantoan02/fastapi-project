# Setup Guide

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 16 or higher
- Redis (optional, for caching)
- Git

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/fastapi-project.git
cd fastapi-project
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (includes testing tools)
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
APP_NAME=FastAPI Project
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-here

DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fastapi_db
REDIS_URL=redis://localhost:6379/0

JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CORS_ORIGINS=["http://localhost:3000"]
```

### 5. Setup Database

Create PostgreSQL database:
```bash
createdb fastapi_db
```

Run migrations:
```bash
./scripts/migrate.sh upgrade
```

### 6. Run Development Server

```bash
./scripts/start-dev.sh
```

Or manually:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Setup

### Using Docker Compose

```bash
# Start all services (API, PostgreSQL, Redis)
docker compose up -d

# Check logs
docker compose logs -f api

# Stop services
docker compose down

# Remove volumes (clean database)
docker compose down -v
```

### Building Custom Image

```bash
docker build -t fastapi-project:latest .
docker run -p 8000:8000 --env-file .env fastapi-project:latest
```

## IDE Setup

### VSCode

Recommended extensions:
- Python
- Pylance
- Ruff

Settings (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

### PyCharm

1. Set Python interpreter to `.venv`
2. Mark `src` as Sources Root
3. Enable Ruff integration

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Check connection string
psql postgresql://user:password@localhost:5432/fastapi_db
```

### Import Errors

Ensure `PYTHONPATH` includes `src`:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

### Permission Denied on Scripts

```bash
chmod +x scripts/*.sh
```
