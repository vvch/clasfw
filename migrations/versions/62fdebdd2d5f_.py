"""empty message

Revision ID: 62fdebdd2d5f
Revises: 
Create Date: 2019-07-17 17:20:04.051132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '62fdebdd2d5f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('channels',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('mdate', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('cdate', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('priority', sa.Integer(), autoincrement=True, nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), server_default='', nullable=False),
    sa.Column('html', sa.String(), nullable=True),
    sa.Column('html_plain', sa.String(), nullable=True),
    sa.Column('tex', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('models',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('priority', sa.Integer(), autoincrement=True, nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), server_default='', nullable=False),
    sa.Column('author', sa.String(), nullable=False),
    sa.Column('comment', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('quantities',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('mdate', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('cdate', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('priority', sa.Integer(), autoincrement=True, nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), server_default='', nullable=False),
    sa.Column('html', sa.String(), nullable=True),
    sa.Column('html_plain', sa.String(), nullable=True),
    sa.Column('tex', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('amplitudes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('channel_id', sa.Integer(), nullable=True),
    sa.Column('model_id', sa.Integer(), nullable=True),
    sa.Column('q2', sa.Float(), nullable=True),
    sa.Column('w', sa.Float(), nullable=True),
    sa.Column('cos_theta', sa.Float(), nullable=True),
    sa.Column('a0r', sa.Float(), nullable=True),
    sa.Column('a0j', sa.Float(), nullable=True),
    sa.Column('a1r', sa.Float(), nullable=True),
    sa.Column('a1j', sa.Float(), nullable=True),
    sa.Column('a2r', sa.Float(), nullable=True),
    sa.Column('a2j', sa.Float(), nullable=True),
    sa.Column('a3r', sa.Float(), nullable=True),
    sa.Column('a3j', sa.Float(), nullable=True),
    sa.Column('a4r', sa.Float(), nullable=True),
    sa.Column('a4j', sa.Float(), nullable=True),
    sa.Column('a5r', sa.Float(), nullable=True),
    sa.Column('a5j', sa.Float(), nullable=True),
    sa.Column('a6r', sa.Float(), nullable=True),
    sa.Column('a6j', sa.Float(), nullable=True),
    sa.Column('a7r', sa.Float(), nullable=True),
    sa.Column('a7j', sa.Float(), nullable=True),
    sa.Column('a8r', sa.Float(), nullable=True),
    sa.Column('a8j', sa.Float(), nullable=True),
    sa.Column('a9r', sa.Float(), nullable=True),
    sa.Column('a9j', sa.Float(), nullable=True),
    sa.Column('a10r', sa.Float(), nullable=True),
    sa.Column('a10j', sa.Float(), nullable=True),
    sa.Column('a11r', sa.Float(), nullable=True),
    sa.Column('a11j', sa.Float(), nullable=True),
    sa.Column('sigma_u', sa.Float(), nullable=True),
    sa.Column('sigma_tt', sa.Float(), nullable=True),
    sa.Column('sigma_tl', sa.Float(), nullable=True),
    sa.Column('sigma_tlp', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
    sa.ForeignKeyConstraint(['model_id'], ['models.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('channel_id', 'model_id', 'q2', 'w', 'cos_theta', name='grid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('amplitudes')
    op.drop_table('quantities')
    op.drop_table('models')
    op.drop_table('channels')
    # ### end Alembic commands ###