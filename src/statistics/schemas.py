from pydantic import BaseModel
from datetime import date

from src.categories.schemas import CategoryOut


class DashboardStats(BaseModel):
    current_balance: float
    last_month_income: float
    last_month_expenses: float

class CategoryStat(BaseModel):
    category: CategoryOut
    total_amount: float
    percentage: float

class DailyStat(BaseModel):
    date: date
    income: float
    expense: float