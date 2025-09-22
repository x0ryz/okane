from datetime import datetime
from pydantic import BaseModel

class TransactionCreate(BaseModel):
    type: str
    name: str
    amount: float
    date: datetime


class TransactionOut(BaseModel):
    id: int
    type: str
    name: str
    amount: float

    class Config:
        from_attributes = True


class TransactionDetail(TransactionOut):
    date: datetime
