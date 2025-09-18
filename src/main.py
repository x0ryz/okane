from fastapi import FastAPI

from src.auth.routes import router as auth_router

app = FastAPI(title="Okane API")

app.include_router(auth_router)