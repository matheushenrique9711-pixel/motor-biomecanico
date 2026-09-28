"""Initial schema with all ORM models

Revision ID: 001
Revises:
Create Date: 2026-09-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create patients table
    op.create_table(
        'patients',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('gender', sa.String(20), nullable=False),
        sa.Column('main_complaint', sa.Text(), nullable=False),
        sa.Column('medical_history', sa.Text(), nullable=True),
        sa.Column('current_medications', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('patient_id'),
    )
    op.create_index('ix_patients_patient_id', 'patients', ['patient_id'])
    op.create_index('ix_patients_name', 'patients', ['name'])

    # Create clinical_cases table
    op.create_table(
        'clinical_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', sa.String(50), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('CREATED', 'SCANNING', 'ANALYZED', 'SUGGESTIONS_GENERATED',
                                   'SUGGESTIONS_REVIEWED', 'ADJUSTMENTS_CONFIRMED',
                                   'GEOMETRY_GENERATED', 'READY_FOR_EXPORT', 'EXPORTED',
                                   'PRINTED', 'DELIVERED', 'FEEDBACK_COLLECTED', 'ARCHIVED',
                                   name='casestatusenum'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('scan_image_path', sa.String(500), nullable=True),
        sa.Column('scan_metadata', postgresql.JSONB(), nullable=True),
        sa.Column('biomechanical_profile', postgresql.JSONB(), nullable=True),
        sa.Column('analysis_confidence', sa.Float(), nullable=True),
        sa.Column('analysis_notes', sa.Text(), nullable=True),
        sa.Column('primary_condition', sa.String(100), nullable=True),
        sa.Column('secondary_conditions', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('suggestions', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('insole_parameters', postgresql.JSONB(), nullable=True),
        sa.Column('clinician_id', sa.String(100), nullable=True),
        sa.Column('clinician_notes', sa.Text(), nullable=True),
        sa.Column('parameters_modified_by_clinician', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('stl_file_path', sa.String(500), nullable=True),
        sa.Column('stl_generated_at', sa.DateTime(), nullable=True),
        sa.Column('geometry_notes', sa.Text(), nullable=True),
        sa.Column('clinical_feedback', sa.Text(), nullable=True),
        sa.Column('patient_feedback', sa.Text(), nullable=True),
        sa.Column('feedback_collected_at', sa.DateTime(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('issues_encountered', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('tags', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('learning_case', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('case_id'),
    )
    op.create_index('ix_cases_case_id', 'clinical_cases', ['case_id'])
    op.create_index('ix_cases_patient_id', 'clinical_cases', ['patient_id'])
    op.create_index('ix_cases_status', 'clinical_cases', ['status'])
    op.create_index('ix_cases_created_at', 'clinical_cases', ['created_at'])

    # Create adjustment_history table
    op.create_table(
        'adjustment_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('adjustment_type', sa.String(50), nullable=False),
        sa.Column('previous_parameters', postgresql.JSONB(), nullable=False),
        sa.Column('new_parameters', postgresql.JSONB(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('modified_by', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['clinical_cases.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_adj_case_id', 'adjustment_history', ['case_id'])
    op.create_index('ix_adj_created_at', 'adjustment_history', ['created_at'])

    # Create case_analyses table
    op.create_table(
        'case_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('foot_length', sa.Float(), nullable=True),
        sa.Column('foot_width', sa.Float(), nullable=True),
        sa.Column('arch_index', sa.Float(), nullable=True),
        sa.Column('contact_pressure_map', postgresql.JSONB(), nullable=True),
        sa.Column('gait_analysis_data', postgresql.JSONB(), nullable=True),
        sa.Column('foot_type', sa.String(50), nullable=True),
        sa.Column('pronation_level', sa.String(50), nullable=True),
        sa.Column('plantar_pressure_distribution', postgresql.JSONB(), nullable=True),
        sa.Column('analyzer_version', sa.String(20), nullable=True),
        sa.Column('analysis_algorithm', sa.String(100), nullable=True),
        sa.Column('raw_image_data', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_analysis_case_id', 'case_analyses', ['case_id'])
    op.create_index('ix_analysis_created_at', 'case_analyses', ['created_at'])

    # Create case_notes table
    op.create_table(
        'case_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('note_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('author_id', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_notes_case_id', 'case_notes', ['case_id'])
    op.create_index('ix_notes_created_at', 'case_notes', ['created_at'])

    # Create case_files table
    op.create_table(
        'case_files',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('case_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('uploaded_by', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_files_case_id', 'case_files', ['case_id'])
    op.create_index('ix_files_created_at', 'case_files', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_files_created_at', table_name='case_files')
    op.drop_index('ix_files_case_id', table_name='case_files')
    op.drop_table('case_files')
    op.drop_index('ix_notes_created_at', table_name='case_notes')
    op.drop_index('ix_notes_case_id', table_name='case_notes')
    op.drop_table('case_notes')
    op.drop_index('ix_analysis_created_at', table_name='case_analyses')
    op.drop_index('ix_analysis_case_id', table_name='case_analyses')
    op.drop_table('case_analyses')
    op.drop_index('ix_adj_created_at', table_name='adjustment_history')
    op.drop_index('ix_adj_case_id', table_name='adjustment_history')
    op.drop_table('adjustment_history')
    op.drop_index('ix_cases_created_at', table_name='clinical_cases')
    op.drop_index('ix_cases_status', table_name='clinical_cases')
    op.drop_index('ix_cases_patient_id', table_name='clinical_cases')
    op.drop_index('ix_cases_case_id', table_name='clinical_cases')
    op.drop_table('clinical_cases')
    op.drop_index('ix_patients_name', table_name='patients')
    op.drop_index('ix_patients_patient_id', table_name='patients')
    op.drop_table('patients')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
