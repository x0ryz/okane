"""seed_categories

Revision ID: 31abc075dfc8
Revises: fcdb341d57c8
Create Date: 2025-11-26 21:01:12.399264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '31abc075dfc8'
down_revision: Union[str, Sequence[str], None] = 'fcdb341d57c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    categories_table = table(
        'categories',
        column('id', sa.Integer),
        column('name', sa.String),
        column('user_id', sa.Integer),
        column('color', sa.String),
        column('icon', sa.String)
    )

    seed_data = [
        {'name': 'Продукти', 'user_id': None, 'color': '#FF5733', 'icon': '🍔'},
        {'name': 'Транспорт', 'user_id': None, 'color': '#3498DB', 'icon': '🚌'},
        {'name': 'Житло', 'user_id': None, 'color': '#9B59B6', 'icon': '🏠'},
        {'name': 'Кафе', 'user_id': None, 'color': '#F1C40F', 'icon': '☕'},
        {'name': 'Розваги', 'user_id': None, 'color': '#E74C3C', 'icon': '🎬'},
        {'name': 'Здоров’я', 'user_id': None, 'color': '#2ECC71', 'icon': '💊'},
        {'name': 'Зарплата', 'user_id': None, 'color': '#27AE60', 'icon': '💰'},
    ]

    op.bulk_insert(categories_table, seed_data)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM categories WHERE user_id IS NULL")
