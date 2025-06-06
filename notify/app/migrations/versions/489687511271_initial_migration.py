"""Initial migration

Revision ID: 489687511271
Revises: 
Create Date: 2025-05-24 21:50:25.419210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '489687511271'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('email_tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('subject', sa.String(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.Column('recipient_email', sa.String(), nullable=True),
    sa.Column('send_time', sa.DateTime(), nullable=True),
    sa.Column('is_sent', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_tasks_id'), 'email_tasks', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_email_tasks_id'), table_name='email_tasks')
    op.drop_table('email_tasks')
    # ### end Alembic commands ###
