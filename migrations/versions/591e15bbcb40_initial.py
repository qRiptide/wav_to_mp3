"""initial

Revision ID: 591e15bbcb40
Revises: 
Create Date: 2023-06-09 12:30:50.651638

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '591e15bbcb40'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('username', sa.String(), nullable=False),
                    sa.Column('uuid', sa.Uuid(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id'),
                    sa.UniqueConstraint('username'),
                    sa.UniqueConstraint('uuid')
                    )
    op.create_table('mp3_record',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('uuid', sa.Uuid(), nullable=False),
                    sa.Column('path', sa.String(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('id')
                    )


def downgrade() -> None:
    op.drop_table('mp3_record')
    op.drop_table('users')
