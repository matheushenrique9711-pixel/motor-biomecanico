"""
SQLAlchemy ORM models for database persistence.
Maps clinical case data to PostgreSQL tables.
"""

from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, Boolean,
    JSON, ForeignKey, Table, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

from app.database.config import Base


class CaseStatusEnum(str, enum.Enum):
    """Case status enumeration."""
    CREATED = "created"
    SCANNING = "scanning"
    ANALYZED = "analyzed"
    SUGGESTIONS_GENERATED = "suggestions_generated"
    SUGGESTIONS_REVIEWED = "suggestions_reviewed"
    ADJUSTMENTS_CONFIRMED = "adjustments_confirmed"
    GEOMETRY_GENERATED = "geometry_generated"
    READY_FOR_EXPORT = "ready_for_export"
    EXPORTED = "exported"
    PRINTED = "printed"
    DELIVERED = "delivered"
    FEEDBACK_COLLECTED = "feedback_collected"
    ARCHIVED = "archived"


class Patient(Base):
    """
    Patient information table.
    Stores patient demographics and contact information.
    """
    __tablename__ = "patients"
    __table_args__ = (
        Index("ix_patients_patient_id", "patient_id"),
        Index("ix_patients_name", "name"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(String(50), unique=True, nullable=False, index=True)

    # Demographics
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)

    # Clinical info
    main_complaint = Column(Text, nullable=False)
    medical_history = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)

    # Contact
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cases = relationship("ClinicalCase", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient {self.patient_id} - {self.name}>"


class ClinicalCase(Base):
    """
    Clinical case table.
    Stores complete case information from intake through delivery.
    """
    __tablename__ = "clinical_cases"
    __table_args__ = (
        Index("ix_cases_case_id", "case_id"),
        Index("ix_cases_patient_id", "patient_id"),
        Index("ix_cases_status", "status"),
        Index("ix_cases_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(50), unique=True, nullable=False, index=True)

    # Patient reference
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    patient = relationship("Patient", back_populates="cases")

    # Status and timestamps
    status = Column(
        SQLEnum(CaseStatusEnum),
        default=CaseStatusEnum.CREATED,
        nullable=False,
        index=True
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ========== SCAN DATA ==========
    scan_image_path = Column(String(500), nullable=True)
    scan_metadata = Column(JSONB, nullable=True)

    # ========== BIOMECHANICAL ANALYSIS ==========
    biomechanical_profile = Column(JSONB, nullable=True)
    analysis_confidence = Column(Float, nullable=True)
    analysis_notes = Column(Text, nullable=True)

    # ========== CLINICAL SUGGESTIONS ==========
    primary_condition = Column(String(100), nullable=True)
    secondary_conditions = Column(JSONB, default=list, nullable=False)
    suggestions = Column(JSONB, default=list, nullable=False)

    # ========== ADJUSTMENTS ==========
    insole_parameters = Column(JSONB, nullable=True)
    clinician_id = Column(String(100), nullable=True)
    clinician_notes = Column(Text, nullable=True)
    parameters_modified_by_clinician = Column(Boolean, default=False)

    # ========== 3D GEOMETRY & EXPORT ==========
    stl_file_path = Column(String(500), nullable=True)
    stl_generated_at = Column(DateTime, nullable=True)
    geometry_notes = Column(Text, nullable=True)

    # ========== FEEDBACK ==========
    clinical_feedback = Column(Text, nullable=True)
    patient_feedback = Column(Text, nullable=True)
    feedback_collected_at = Column(DateTime, nullable=True)

    # ========== QUALITY CONTROL ==========
    quality_score = Column(Float, nullable=True)
    issues_encountered = Column(JSONB, default=list, nullable=False)

    # ========== CLASSIFICATION ==========
    tags = Column(JSONB, default=list, nullable=False)
    learning_case = Column(Boolean, default=False)

    # Relationships
    adjustments_history = relationship(
        "AdjustmentHistory",
        back_populates="case",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Case {self.case_id} - {self.status}>"

    def is_ready_for_geometry_generation(self) -> bool:
        """Check if case is ready for 3D geometry generation."""
        return (
            self.status in [CaseStatusEnum.ADJUSTMENTS_CONFIRMED, CaseStatusEnum.GEOMETRY_GENERATED]
            and self.insole_parameters is not None
        )

    def is_ready_for_export(self) -> bool:
        """Check if case is ready for STL export."""
        return (
            self.status.value >= CaseStatusEnum.GEOMETRY_GENERATED.value
            and self.stl_file_path is not None
        )

    def has_complete_feedback(self) -> bool:
        """Check if case has complete feedback."""
        return (
            self.status == CaseStatusEnum.FEEDBACK_COLLECTED
            and self.clinical_feedback is not None
            and self.patient_feedback is not None
        )


class AdjustmentHistory(Base):
    """
    Audit trail for parameter adjustments.
    Tracks all modifications made to a case's insole parameters.
    """
    __tablename__ = "adjustment_history"
    __table_args__ = (
        Index("ix_adj_case_id", "case_id"),
        Index("ix_adj_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("clinical_cases.id"), nullable=False)
    case = relationship("ClinicalCase", back_populates="adjustments_history")

    # Adjustment details
    adjustment_type = Column(String(50), nullable=False)  # "system" or "clinician"
    previous_parameters = Column(JSONB, nullable=False)
    new_parameters = Column(JSONB, nullable=False)
    reason = Column(Text, nullable=True)

    # Who made the change
    modified_by = Column(String(100), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AdjustmentHistory {self.id} - {self.adjustment_type}>"


class CaseAnalysis(Base):
    """
    Detailed analysis results.
    Stores in-depth biomechanical analysis data for each case.
    """
    __tablename__ = "case_analyses"
    __table_args__ = (
        Index("ix_analysis_case_id", "case_id"),
        Index("ix_analysis_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("clinical_cases.id"), nullable=False)

    # Analysis data
    foot_length = Column(Float, nullable=True)
    foot_width = Column(Float, nullable=True)
    arch_index = Column(Float, nullable=True)
    contact_pressure_map = Column(JSONB, nullable=True)
    gait_analysis_data = Column(JSONB, nullable=True)

    # Extracted metrics
    foot_type = Column(String(50), nullable=True)  # flat, normal, cavus
    pronation_level = Column(String(50), nullable=True)  # under, neutral, over
    plantar_pressure_distribution = Column(JSONB, nullable=True)

    # Analysis metadata
    analyzer_version = Column(String(20), nullable=True)
    analysis_algorithm = Column(String(100), nullable=True)
    raw_image_data = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CaseAnalysis {self.case_id}>"


class CaseNotes(Base):
    """
    Clinical notes and observations.
    Allows clinicians to add timestamped notes throughout case lifecycle.
    """
    __tablename__ = "case_notes"
    __table_args__ = (
        Index("ix_notes_case_id", "case_id"),
        Index("ix_notes_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("clinical_cases.id"), nullable=False)

    # Note content
    note_type = Column(String(50), nullable=False)  # observation, adjustment, follow-up, etc
    content = Column(Text, nullable=False)

    # Author and timestamp
    author_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CaseNote {self.case_id} - {self.note_type}>"


class CaseFile(Base):
    """
    File attachments for cases.
    Tracks uploaded files (images, documents, etc.) associated with cases.
    """
    __tablename__ = "case_files"
    __table_args__ = (
        Index("ix_files_case_id", "case_id"),
        Index("ix_files_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("clinical_cases.id"), nullable=False)

    # File info
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # image, document, stl, etc
    file_size = Column(Integer, nullable=False)

    # Metadata
    description = Column(Text, nullable=True)
    uploaded_by = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CaseFile {self.file_name} - {self.file_type}>"


class FootConditionPreset(Base):
    """
    Pre-configured foot condition templates.
    Stores common foot conditions and recommended insole parameters for quick application.
    """
    __tablename__ = "foot_condition_presets"
    __table_args__ = (
        Index("ix_preset_name", "condition_name"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Condition info
    condition_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)
    severity_level = Column(String(50), nullable=False)  # leve, moderada, severa

    # Clinical information
    clinical_indicators = Column(JSONB, nullable=False)  # List of indicators
    common_complaints = Column(JSONB, nullable=False)  # List of common patient complaints

    # Recommended parameters
    recommended_parameters = Column(JSONB, nullable=False)  # Insole parameters
    arch_support_level = Column(String(50), nullable=False)  # baixo, médio, alto
    heel_height_mm = Column(Float, nullable=False)
    material_recommendation = Column(String(100), nullable=False)  # EVA, poliuretano, etc

    # Visual reference
    illustration_path = Column(String(500), nullable=True)
    reference_image_url = Column(String(500), nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<FootConditionPreset {self.condition_name}>"
