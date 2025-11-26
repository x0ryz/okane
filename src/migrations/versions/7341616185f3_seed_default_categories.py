"""seed_default_categories

Revision ID: 7341616185f3
Revises: e742714df92a
Create Date: 2025-11-26 19:55:39.437727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '7341616185f3'
down_revision: Union[str, Sequence[str], None] = 'e742714df92a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    categories_table = table(
        'categories',
        column('id', sa.Integer),
        column('name', sa.String),
        column('user_id', sa.Integer)
    )

    seed_data = [
        {'name': 'Продукти', 'user_id': None},
        {'name': 'Транспорт', 'user_id': None},
        {'name': 'Житло', 'user_id': None},
        {'name': 'Кафе та ресторани', 'user_id': None},
        {'name': 'Розваги', 'user_id': None},
        {'name': 'Здоров’я', 'user_id': None},
        {'name': 'Освіта', 'user_id': None},
        {'name': 'Подарунки', 'user_id': None},
        {'name': 'Зарплата', 'user_id': None},
    ]

    op.bulk_insert(categories_table, seed_data)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "DELETE FROM categories WHERE user_id IS NULL"
    )
