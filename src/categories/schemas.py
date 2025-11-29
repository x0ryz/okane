from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str
    color: str = "#CCCCCC"
    icon: str = "📦"


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    user_id: int | None

    model_config = ConfigDict(from_attributes=True)