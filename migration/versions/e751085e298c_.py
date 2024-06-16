"""empty message

Revision ID: e751085e298c
Revises: 01a0ff7692ba
Create Date: 2024-04-29 18:40:45.038998

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e751085e298c'
down_revision: Union[str, None] = '01a0ff7692ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('TypeCategory',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('CategorySong', sa.Column('type_category', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'CategorySong', 'TypeCategory', ['type_category'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'CategorySong', type_='foreignkey')
    op.drop_column('CategorySong', 'type_category')
    op.drop_table('TypeCategory')
    # ### end Alembic commands ###