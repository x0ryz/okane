# Okane API

Personal finance management API built with FastAPI, PostgreSQL, and Redis.

## Features

- JWT-based authentication with refresh tokens
- Transaction management (income/expense tracking)
- Category management (default and custom categories)
- Redis-based session management
- Database migrations with Alembic
- Secure password hashing with Argon2

## Tech Stack

`FastAPI` `PostgreSQL` `Redis` `SQLAlchemy` `Alembic` `JWT` `Argon2`

## Prerequisites

- Python 3.11+
- PostgreSQL
- Redis

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/x0ryz/okane.git
cd okane
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create `.env` file:**
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/okane
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
REDIS_HOST=localhost
REDIS_PORT=6379
```

> **Note:** Generate a secure SECRET_KEY with: `openssl rand -hex 32`

5. **Run migrations:**
```bash
alembic upgrade head
```

6. **Start the server:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`

## Docker Setup (Optional)

```bash
docker compose up -d
```

This will start PostgreSQL and Redis containers.

## API Documentation

Interactive API docs available at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
