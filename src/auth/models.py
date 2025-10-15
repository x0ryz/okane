from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base

if TYPE_CHECKING:
    from src.transactions.models import Transaction
    from src.categories.models import Category

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    transactions: Mapped[list[Transaction]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    categories: Mapped[list[Category]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )