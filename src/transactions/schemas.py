from datetime import datetime
from pydantic import BaseModel, ConfigDict

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

    model_config = ConfigDict(from_attributes=True)


class TransactionDetail(TransactionOut):
    date: datetime
