"""empty message

Revision ID: 6e5e97c6c9bb
Revises: 357087f72d47
Create Date: 2024-05-11 18:55:16.482808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e5e97c6c9bb'
down_revision: Union[str, None] = '357087f72d47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('PiggyBankGames',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('PiggyBankGroups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('PiggyBankTypesGame',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('PiggyBankGroupForGame',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['PiggyBankGames.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['PiggyBankGroups.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('PiggyBankTypesGamesForGame',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['PiggyBankGames.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['PiggyBankTypesGame.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('PiggyBankTypesGamesForGame')
    op.drop_table('PiggyBankGroupForGame')
    op.drop_table('PiggyBankTypesGame')
    op.drop_table('PiggyBankGroups')
    op.drop_table('PiggyBankGames')
    # ### end Alembic commands ###
