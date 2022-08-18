"""empty message

Revision ID: 2e507e2be329
Revises: 
Create Date: 2022-08-17 23:58:31.659079

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2e507e2be329'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('strt_time', sa.String(), nullable=True))
    op.drop_column('shows', 'start_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('shows', 'strt_time')
    # ### end Alembic commands ###
