from pydantic import BaseModel
from datetime import date

from src.categories.schemas import CategoryRead


class DashboardStats(BaseModel):
    current_balance: float
    last_month_income: float
    last_month_expenses: float

class CategoryStat(BaseModel):
    category: CategoryRead
    total_amount: float
    percentage: float

class DailyStat(BaseModel):
    date: date
    income: float
    expense: float