"""empty message

Revision ID: f5434f0804d6
Revises: 0aa12e9f36ad
Create Date: 2024-05-18 00:35:27.122606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5434f0804d6'
down_revision: Union[str, None] = '0aa12e9f36ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
