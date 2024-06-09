"""empty message

Revision ID: 41a1930b3e81
Revises: b3f9fbf10331
Create Date: 2024-01-26 19:19:05.917729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41a1930b3e81'
down_revision: Union[str, None] = 'b3f9fbf10331'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
