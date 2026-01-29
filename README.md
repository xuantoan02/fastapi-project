# FastAPI Project

A production-ready FastAPI application with JWT authentication, PostgreSQL, and Raw SQL queries.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **Raw SQL Queries** - Direct SQL queries with SQLAlchemy Core (no ORM overhead)
- **JWT Authentication** - Secure token-based authentication
- **Alembic** - Database migrations
- **Docker** - Containerized deployment
- **CI/CD** - GitHub Actions workflows

## Project Structure

```
fastapi-project/
├── src/
│   ├── main.py              # Application entry point
│   ├── api/v1/              # API endpoints (versioned)
│   │   └── endpoints/       # Route handlers
│   ├── core/                # Configuration & security
│   ├── db/                  # Database setup & helpers
│   │   ├── session.py       # Connection pool & raw SQL helpers
│   │   └── orm_models.py    # ORM models (for Alembic only)
│   ├── dependencies/        # FastAPI dependencies
│   ├── middleware/          # CORS, error handling
│   ├── models/              # Data classes (dataclasses)
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic & SQL queries
├── tests/                   # Test suite
├── alembic/                 # Database migrations
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
├── .github/workflows/       # CI/CD pipelines
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container build
├── requirements.txt         # Dependencies
└── pyproject.toml           # Project configuration
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fastapi-project.git
   cd fastapi-project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run database migrations**
   ```bash
   ./scripts/migrate.sh upgrade
   ```

6. **Start development server**
   ```bash
   ./scripts/start-dev.sh
   ```

   The API will be available at `http://localhost:8000`

### Using Docker

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f api

# Stop services
docker compose down
```

## API Documentation

When running in development mode (`DEBUG=true`), API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login and get token |
| GET | `/api/v1/auth/me` | Get current user |
| GET | `/api/v1/users/` | List users (admin) |
| GET | `/api/v1/items/` | List user items |
| POST | `/api/v1/items/` | Create item |
| GET | `/api/v1/health/` | Health check |

## Configuration

Environment variables (set in `.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_ENV` | Environment (development/production) | development |
| `DEBUG` | Enable debug mode | false |
| `SECRET_KEY` | Application secret key | - |
| `DATABASE_URL` | PostgreSQL connection URL | - |
| `REDIS_URL` | Redis connection URL | - |
| `JWT_SECRET_KEY` | JWT signing key | - |
| `CORS_ORIGINS` | Allowed CORS origins | - |

## Database Layer

### Raw SQL Approach

This project uses **raw SQL queries** instead of ORM for better performance and control:

```python
# src/db/session.py - Helper functions
async def fetch_one(conn, query, params)   # Single row
async def fetch_all(conn, query, params)   # Multiple rows
async def fetch_scalar(conn, query, params) # Single value
async def execute_query(conn, query, params) # INSERT/UPDATE/DELETE
```

### Service Layer Example

```python
# src/services/user_service.py
class UserService:
    async def get_by_id(self, user_id: int) -> User:
        query = """
            SELECT id, email, hashed_password, full_name,
                   is_active, is_superuser, created_at, updated_at
            FROM users WHERE id = :user_id
        """
        row = await fetch_one(self.db, query, {"user_id": user_id})
        if not row:
            raise NotFoundError("User")
        return User.from_row(row)
```

### Data Classes

Models are simple Python dataclasses (not ORM models):

```python
# src/models/user.py
@dataclass
class User:
    id: int
    email: str
    hashed_password: str
    full_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "User":
        return cls(**row)
```

### Migrations

ORM models are kept separately in `src/db/orm_models.py` **only for Alembic migrations**:

```bash
# Create new migration
./scripts/migrate.sh revision "add users table"

# Apply migrations
./scripts/migrate.sh upgrade

# Rollback
./scripts/migrate.sh downgrade
```

## Development

### Running Tests

```bash
# Run all tests
./scripts/test.sh

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Lint code
ruff check src/

# Format code
ruff format src/

# Type checking
mypy src/
```

## Deployment

### Production Checklist

- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure proper `CORS_ORIGINS`
- [ ] Set up SSL/TLS
- [ ] Configure database connection pooling
- [ ] Set up monitoring and logging

### Docker Production

```bash
docker build -t fastapi-project:latest .
docker run -p 8000:8000 --env-file .env fastapi-project:latest
```

## Architecture

```
┌─────────────────────────────────┐
│         API Layer               │
│     (FastAPI Endpoints)         │
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│      Dependencies Layer         │
│  (Auth, DB Connection, etc.)    │
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│        Service Layer            │
│   (Business Logic + Raw SQL)    │
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│        Database Layer           │
│  (PostgreSQL + AsyncConnection) │
└─────────────────────────────────┘
```

## License

MIT License - see [LICENSE](LICENSE) for details.
