from datetime import datetime
from pydantic import BaseModel

class CreateTransaction(BaseModel):
    type: str
    name: str
    amount: float
    date: datetime

class TranactionsOut(BaseModel):
    type: str
    name: str
    amount: float

    class Config:
        orm_mode: True