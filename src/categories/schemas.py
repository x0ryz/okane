from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str

class CategoryOut(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)