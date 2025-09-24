from pydantic import BaseModel

class CreateCategory(BaseModel):
    name: str