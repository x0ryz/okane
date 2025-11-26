from datetime import datetime
from typing import Literal
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, model_validator, Field

from src.categories.schemas import CategoryOut


class TransactionCreate(BaseModel):
    type: Literal["income", "expense"] = "expense"
    name: str
    amount: Decimal
    category_id: int
    date: datetime


class TransactionOut(BaseModel):
    id: int
    type: str
    name: str
    amount: Decimal
    date: datetime
    category: CategoryOut | None = None

    model_config = ConfigDict(from_attributes=True)

    # @model_validator(mode='after')
    # def adjust_sign_for_expense(self):
    #     if self.type == "expense" and self.amount > 0:
    #         self.amount = -self.amount
    #     return self

class TransactionUpdate(BaseModel):
    type: Literal["income", "expense"]
    name: str | None = Field(None, min_length=2, max_length=50)
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    category_id: int | None = None
    date: datetime | None = None