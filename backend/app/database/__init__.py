"""
Database module for Motor Biomecânico.
Provides ORM models, configuration, and initialization.
"""

from app.database.config import Base, engine, SessionLocal, get_db, init_db, drop_db
from app.database.models import (
    Patient, ClinicalCase, AdjustmentHistory, CaseAnalysis,
    CaseNotes, CaseFile, CaseStatusEnum
)
from app.database.repository import (
    PatientRepository, ClinicalCaseRepository, AdjustmentHistoryRepository,
    CaseAnalysisRepository, CaseNotesRepository, CaseFileRepository
)
from app.database.initialize import initialize_database, get_database_info

__all__ = [
    # Config
    'Base', 'engine', 'SessionLocal', 'get_db', 'init_db', 'drop_db',
    # Models
    'Patient', 'ClinicalCase', 'AdjustmentHistory', 'CaseAnalysis',
    'CaseNotes', 'CaseFile', 'CaseStatusEnum',
    # Repositories
    'PatientRepository', 'ClinicalCaseRepository', 'AdjustmentHistoryRepository',
    'CaseAnalysisRepository', 'CaseNotesRepository', 'CaseFileRepository',
    # Initialization
    'initialize_database', 'get_database_info',
]
