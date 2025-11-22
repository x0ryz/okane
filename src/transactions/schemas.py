from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, model_validator

from src.categories.schemas import CategoryOut


class TransactionCreate(BaseModel):
    type: Literal["income", "expense"] = "expense"
    name: str
    amount: float
    category_id: int
    date: datetime


class TransactionOut(BaseModel):
    id: int
    type: str
    name: str
    amount: float
    date: datetime
    category: CategoryOut

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='after')
    def adjust_sign_for_expense(self):
        if self.type == "expense" and self.amount > 0:
            self.amount *= -self.amount
        return self
