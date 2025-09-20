from __future__ import annotations

from datetime import datetime

from sqlalchemy import Integer, ForeignKey, String, DateTime, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    type: Mapped[str] = mapped_column(Enum("income", "expense", name="transaction_type"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)

    date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="transactions")
