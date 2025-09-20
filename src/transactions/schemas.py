from datetime import datetime
from pydantic import BaseModel

class CreateTransaction(BaseModel):
    type: str
    name: str
    amount: float
    date: datetime