from datetime import date, timedelta, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import joinedload

from src.database import get_session
from src.statistics.schemas import CategoryStat,DailyStat
from src.auth.models import User
from src.transactions.models import Transaction
from src.categories.models import Category
from src.auth.depends import read_user

router = APIRouter(prefix="/statistics", tags=["Statistics"])

@router.get("/categories", response_model=list[CategoryStat])
async def get_stats_by_categories(
        start_date: date = date.today() - timedelta(days=7),
        end_date: date = date.today(),
        user: User = Depends(read_user),
        session: AsyncSession = Depends(get_session)
) -> list[CategoryStat]:
    query = (
        select(Category, func.sum(Transaction.amount))
        .join(Transaction.category)
        .where(
            and_(
                Transaction.user_id == user.id,
                func.date(Transaction.date) >= start_date,
                func.date(Transaction.date) <= end_date,
                Transaction.type == "expense",

                or_(
                    Category.user_id == None,
                    Category.user_id == user.id
                )
            )
        )
        .group_by(Category.id)
    )

    result = await session.execute(query)
    rows = result.all()

    total_sum = sum(float(row[1]) for row in rows)

    stats = []
    for category_obj, amount in rows:
        amount = float(amount or 0)
        percent = round((amount / total_sum) * 100, 1) if total_sum > 0 else 0

        stats.append(CategoryStat(
            category=category_obj,
            total_amount=amount,
            percentage=percent
        ))

    return stats


@router.get("/history", response_model=list[DailyStat])
async def get_stats_by_history(
        start_date: date = date.today() - timedelta(days=7),
        end_date: date = date.today(),
        user: User = Depends(read_user),
        session: AsyncSession = Depends(get_session)
):
    stmt = (
        select(
            func.date(Transaction.date).label("day"),
            Transaction.type,
            func.sum(Transaction.amount).label("total")
        )
        .where(
            and_(
                Transaction.user_id == user.id,
                func.date(Transaction.date) >= start_date,
                func.date(Transaction.date) <= end_date
            )
        )
        .group_by(func.date(Transaction.date), Transaction.type)
        .order_by(func.date(Transaction.date))
    )

    result = await session.execute(stmt)
    data = result.all()

    stats_map = {}
    current_date = start_date
    while current_date <= end_date:
        stats_map[current_date] = {"date": current_date, "income": 0, "expense": 0}
        current_date += timedelta(days=1)

    for day, trans_type, total in data:

        if isinstance(day, str):
            day = datetime.strptime(day, "%Y-%m-%d").date()

        if day in stats_map:
            stats_map[day][trans_type] = total

    return list(stats_map.values())