from fastapi import FastAPI

from src.auth.routes import router as auth_router
from src.transactions.routes import router as transactions_router

app = FastAPI(title="Okane API")

app.include_router(auth_router)
app.include_router(transactions_router)