"""Add foot condition presets table

Revision ID: 002
Revises: 001_initial_schema
Create Date: 2026-09-28 16:41:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """Create foot_condition_presets table."""
    op.create_table(
        'foot_condition_presets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('condition_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('severity_level', sa.String(50), nullable=False),
        sa.Column('clinical_indicators', postgresql.JSONB(), nullable=False),
        sa.Column('common_complaints', postgresql.JSONB(), nullable=False),
        sa.Column('recommended_parameters', postgresql.JSONB(), nullable=False),
        sa.Column('arch_support_level', sa.String(50), nullable=False),
        sa.Column('heel_height_mm', sa.Float(), nullable=False),
        sa.Column('material_recommendation', sa.String(100), nullable=False),
        sa.Column('illustration_path', sa.String(500), nullable=True),
        sa.Column('reference_image_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('condition_name')
    )
    op.create_index('ix_preset_name', 'foot_condition_presets', ['condition_name'])


def downgrade():
    """Drop foot_condition_presets table."""
    op.drop_index('ix_preset_name', table_name='foot_condition_presets')
    op.drop_table('foot_condition_presets')
