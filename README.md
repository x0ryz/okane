# Okane API

Personal finance management API built with FastAPI for tracking income and expenses.

## Stack

`Python 3.11` · `FastAPI` · `SQLAlchemy` · `PostgreSQL` · `Redis` · `RabbitMQ` · `Alembic` · `Docker`

## Features

- 🔐 JWT-based authentication with refresh tokens
- 📧 Email verification via RabbitMQ workers
- 💰 Transaction management (income/expense tracking)
- 📊 Categories with custom colors and icons
- 📈 Statistics and dashboard analytics
- 🔄 Password reset functionality
- 🐳 Fully containerized with Docker Compose

## Project Structure

```
src/
├── auth/          # Authentication & user management
├── transactions/  # Income/expense operations
├── categories/    # Category management
├── statistics/    # Analytics and reporting
├── migrations/    # Alembic database migrations
└── worker.py      # Background task worker (emails)
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)

### Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql+asyncpg://okane_user:okane_pass@db:5432/okane_db
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
REDIS_HOST=redis
REDIS_PORT=6379
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
RABBITMQ_USER=guest
RABBITMQ_PASS=guest
RESEND_API=your_resend_api_key
POSTGRES_USER=okane_user
POSTGRES_PASSWORD=okane_pass
POSTGRES_DB=okane_db
```

### Running with Docker

```bash
# Build and start all services
docker compose up -d --build

# Run migrations
docker compose exec app alembic upgrade head
```

The API will be available at `http://localhost:8000`

### Local Development (VS Code DevContainer)

1. Open project in VS Code
2. Install "Dev Containers" extension
3. Press `F1` → "Dev Containers: Reopen in Container"
4. Run migrations: `alembic upgrade head`
5. Start server: `uvicorn src.main:app --reload`

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Key Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get tokens
- `POST /auth/verify` - Verify email with code
- `GET /transactions/` - List transactions (paginated)
- `POST /transactions/` - Create transaction
- `GET /categories/` - List categories
- `GET /statistics/dashboard` - Get dashboard stats

## Development

### Running Tests

```bash
pytest
```

### Creating Migrations

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Services

- **App**: FastAPI application (port 8000)
- **Worker**: FastStream consumer for email sending
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache & session storage (port 6379)
- **RabbitMQ**: Message queue (ports 5672, 15672)

## Deployment

The project includes GitHub Actions workflow for automated deployment via SSH. Configure secrets:
- `HOST` - Server IP
- `USERNAME` - SSH username
- `KEY` - SSH private key
- `PORT` - SSH port
