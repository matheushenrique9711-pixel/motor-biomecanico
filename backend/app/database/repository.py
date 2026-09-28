"""
CRUD Repository layer for database operations.
Provides data access abstraction for all ORM models.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import uuid

from app.database.models import (
    Patient, ClinicalCase, AdjustmentHistory, CaseAnalysis,
    CaseNotes, CaseFile, FootConditionPreset, CaseStatusEnum
)


class PatientRepository:
    """Repository for Patient entity CRUD operations."""

    @staticmethod
    def create(db: Session, patient_id: str, name: str, age: int,
               gender: str, main_complaint: str, medical_history: Optional[str] = None,
               current_medications: Optional[str] = None, phone: Optional[str] = None,
               email: Optional[str] = None) -> Patient:
        """Create a new patient."""
        patient = Patient(
            patient_id=patient_id,
            name=name,
            age=age,
            gender=gender,
            main_complaint=main_complaint,
            medical_history=medical_history,
            current_medications=current_medications,
            phone=phone,
            email=email
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def get_by_id(db: Session, patient_id: str) -> Optional[Patient]:
        """Get patient by UUID."""
        return db.query(Patient).filter(Patient.id == patient_id).first()

    @staticmethod
    def get_by_patient_id(db: Session, patient_id: str) -> Optional[Patient]:
        """Get patient by patient_id (unique string identifier)."""
        return db.query(Patient).filter(Patient.patient_id == patient_id).first()

    @staticmethod
    def list_all(db: Session, limit: int = 50, offset: int = 0) -> List[Patient]:
        """List all patients with pagination."""
        return db.query(Patient).limit(limit).offset(offset).all()

    @staticmethod
    def update(db: Session, patient_id: str, **kwargs) -> Optional[Patient]:
        """Update patient fields."""
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if patient:
            for key, value in kwargs.items():
                if hasattr(patient, key):
                    setattr(patient, key, value)
            db.commit()
            db.refresh(patient)
        return patient

    @staticmethod
    def delete(db: Session, patient_id: str) -> bool:
        """Delete patient (cascades to cases)."""
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if patient:
            db.delete(patient)
            db.commit()
            return True
        return False


class ClinicalCaseRepository:
    """Repository for ClinicalCase entity CRUD operations."""

    @staticmethod
    def create(db: Session, case_id: str, patient_id: str,
               status: CaseStatusEnum = CaseStatusEnum.CREATED) -> ClinicalCase:
        """Create a new clinical case."""
        case = ClinicalCase(
            case_id=case_id,
            patient_id=patient_id,
            status=status
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def get_by_id(db: Session, case_id: str) -> Optional[ClinicalCase]:
        """Get case by UUID."""
        return db.query(ClinicalCase).filter(ClinicalCase.id == case_id).first()

    @staticmethod
    def get_by_case_id(db: Session, case_id: str) -> Optional[ClinicalCase]:
        """Get case by case_id (unique string identifier)."""
        return db.query(ClinicalCase).filter(ClinicalCase.case_id == case_id).first()

    @staticmethod
    def list_by_patient(db: Session, patient_id: str) -> List[ClinicalCase]:
        """Get all cases for a patient."""
        return db.query(ClinicalCase).filter(
            ClinicalCase.patient_id == patient_id
        ).order_by(desc(ClinicalCase.created_at)).all()

    @staticmethod
    def list_by_status(db: Session, status: CaseStatusEnum, limit: int = 50,
                      offset: int = 0) -> List[ClinicalCase]:
        """List cases by status."""
        return db.query(ClinicalCase).filter(
            ClinicalCase.status == status
        ).order_by(desc(ClinicalCase.created_at)).limit(limit).offset(offset).all()

    @staticmethod
    def list_all(db: Session, limit: int = 50, offset: int = 0) -> List[ClinicalCase]:
        """List all cases."""
        return db.query(ClinicalCase).order_by(
            desc(ClinicalCase.created_at)
        ).limit(limit).offset(offset).all()

    @staticmethod
    def update_status(db: Session, case_id: str, status: CaseStatusEnum) -> Optional[ClinicalCase]:
        """Update case status."""
        case = db.query(ClinicalCase).filter(ClinicalCase.case_id == case_id).first()
        if case:
            case.status = status
            case.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(case)
        return case

    @staticmethod
    def update_biomechanical_analysis(db: Session, case_id: str,
                                     biomechanical_profile: dict,
                                     analysis_confidence: float,
                                     analysis_notes: Optional[str] = None) -> Optional[ClinicalCase]:
        """Update biomechanical analysis data."""
        case = db.query(ClinicalCase).filter(ClinicalCase.case_id == case_id).first()
        if case:
            case.biomechanical_profile = biomechanical_profile
            case.analysis_confidence = analysis_confidence
            case.analysis_notes = analysis_notes
            case.status = CaseStatusEnum.ANALYZED
            case.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(case)
        return case

    @staticmethod
    def update_suggestions(db: Session, case_id: str, primary_condition: str,
                          secondary_conditions: list, suggestions: list) -> Optional[ClinicalCase]:
        """Update case suggestions."""
        case = db.query(ClinicalCase).filter(ClinicalCase.case_id == case_id).first()
        if case:
            case.primary_condition = primary_condition
            case.secondary_conditions = secondary_conditions
            case.suggestions = suggestions
            case.status = CaseStatusEnum.SUGGESTIONS_GENERATED
            case.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(case)
        return case

    @staticmethod
    def update_insole_parameters(db: Session, case_id: str, insole_parameters: dict,
                                modified_by_clinician: bool = False,
                                clinician_id: Optional[str] = None,
                                clinician_notes: Optional[str] = None) -> Optional[ClinicalCase]:
        """Update insole parameters."""
        case = db.query(ClinicalCase).filter(ClinicalCase.case_id == case_id).first()
        if case:
            case.insole_parameters = insole_parameters
            case.parameters_modified_by_clinician = modified_by_clinician
            if clinician_id:
                case.clinician_id = clinician_id
            if clinician_notes:
                case.clinician_notes = clinician_notes
            case.status = CaseStatusEnum.ADJUSTMENTS_CONFIRMED
            case.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(case)
        return case

    @staticmethod
    def register_stl_export(db: Session, case_id: str, stl_file_path: str,
                           geometry_notes: Optional[str] = None) -> Optional[ClinicalCase]:
        """Register STL file export."""
        case = db.query(ClinicalCase).filter(ClinicalCase.case_id == case_id).first()
        if case:
            case.stl_file_path = stl_file_path
            case.stl_generated_at = datetime.utcnow()
            case.geometry_notes = geometry_notes
            case.status = CaseStatusEnum.GEOMETRY_GENERATED
            case.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(case)
        return case

    @staticmethod
    def add_feedback(db: Session, case_id: str, clinical_feedback: Optional[str] = None,
                    patient_feedback: Optional[str] = None,
                    quality_score: Optional[float] = None) -> Optional[ClinicalCase]:
        """Add feedback to case."""
        case = db.query(ClinicalCase).filter(ClinicalCase.case_id == case_id).first()
        if case:
            if clinical_feedback:
                case.clinical_feedback = clinical_feedback
            if patient_feedback:
                case.patient_feedback = patient_feedback
            if quality_score is not None:
                case.quality_score = quality_score
            case.feedback_collected_at = datetime.utcnow()
            case.status = CaseStatusEnum.FEEDBACK_COLLECTED
            case.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(case)
        return case

    @staticmethod
    def delete(db: Session, case_id: str) -> bool:
        """Delete case (cascades to related records)."""
        case = db.query(ClinicalCase).filter(ClinicalCase.case_id == case_id).first()
        if case:
            db.delete(case)
            db.commit()
            return True
        return False


class AdjustmentHistoryRepository:
    """Repository for AdjustmentHistory audit trail."""

    @staticmethod
    def create(db: Session, case_id: str, adjustment_type: str,
               previous_parameters: dict, new_parameters: dict,
               modified_by: str, reason: Optional[str] = None) -> AdjustmentHistory:
        """Create adjustment history record."""
        adjustment = AdjustmentHistory(
            case_id=case_id,
            adjustment_type=adjustment_type,
            previous_parameters=previous_parameters,
            new_parameters=new_parameters,
            modified_by=modified_by,
            reason=reason
        )
        db.add(adjustment)
        db.commit()
        db.refresh(adjustment)
        return adjustment

    @staticmethod
    def get_case_history(db: Session, case_id: str) -> List[AdjustmentHistory]:
        """Get all adjustments for a case."""
        return db.query(AdjustmentHistory).filter(
            AdjustmentHistory.case_id == case_id
        ).order_by(AdjustmentHistory.created_at).all()


class CaseAnalysisRepository:
    """Repository for CaseAnalysis detailed results."""

    @staticmethod
    def create(db: Session, case_id: str, **kwargs) -> CaseAnalysis:
        """Create analysis record."""
        analysis = CaseAnalysis(case_id=case_id, **kwargs)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def get_by_case_id(db: Session, case_id: str) -> Optional[CaseAnalysis]:
        """Get analysis for a case."""
        return db.query(CaseAnalysis).filter(CaseAnalysis.case_id == case_id).first()


class CaseNotesRepository:
    """Repository for CaseNotes."""

    @staticmethod
    def create(db: Session, case_id: str, note_type: str, content: str,
               author_id: str) -> CaseNotes:
        """Add note to case."""
        note = CaseNotes(
            case_id=case_id,
            note_type=note_type,
            content=content,
            author_id=author_id
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def get_case_notes(db: Session, case_id: str) -> List[CaseNotes]:
        """Get all notes for a case."""
        return db.query(CaseNotes).filter(
            CaseNotes.case_id == case_id
        ).order_by(CaseNotes.created_at).all()


class CaseFileRepository:
    """Repository for CaseFile attachments."""

    @staticmethod
    def create(db: Session, case_id: str, file_name: str, file_path: str,
               file_type: str, file_size: int, uploaded_by: str,
               description: Optional[str] = None) -> CaseFile:
        """Add file to case."""
        file = CaseFile(
            case_id=case_id,
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            uploaded_by=uploaded_by,
            description=description
        )
        db.add(file)
        db.commit()
        db.refresh(file)
        return file

    @staticmethod
    def get_case_files(db: Session, case_id: str) -> List[CaseFile]:
        """Get all files for a case."""
        return db.query(CaseFile).filter(CaseFile.case_id == case_id).all()

    @staticmethod
    def delete(db: Session, file_id: str) -> bool:
        """Delete file record."""
        file = db.query(CaseFile).filter(CaseFile.id == file_id).first()
        if file:
            db.delete(file)
            db.commit()
            return True
        return False


class PresetRepository:
    """Repository for FootConditionPreset templates."""

    @staticmethod
    def create(db: Session, condition_name: str, description: str,
               severity_level: str, clinical_indicators: list,
               common_complaints: list, recommended_parameters: dict,
               arch_support_level: str, heel_height_mm: float,
               material_recommendation: str, illustration_path: Optional[str] = None,
               reference_image_url: Optional[str] = None) -> FootConditionPreset:
        """Create a new foot condition preset."""
        preset = FootConditionPreset(
            condition_name=condition_name,
            description=description,
            severity_level=severity_level,
            clinical_indicators=clinical_indicators,
            common_complaints=common_complaints,
            recommended_parameters=recommended_parameters,
            arch_support_level=arch_support_level,
            heel_height_mm=heel_height_mm,
            material_recommendation=material_recommendation,
            illustration_path=illustration_path,
            reference_image_url=reference_image_url
        )
        db.add(preset)
        db.commit()
        db.refresh(preset)
        return preset

    @staticmethod
    def get_all(db: Session) -> List[FootConditionPreset]:
        """Get all foot condition presets."""
        return db.query(FootConditionPreset).order_by(FootConditionPreset.condition_name).all()

    @staticmethod
    def get_by_name(db: Session, condition_name: str) -> Optional[FootConditionPreset]:
        """Get preset by condition name."""
        return db.query(FootConditionPreset).filter(
            FootConditionPreset.condition_name == condition_name
        ).first()

    @staticmethod
    def get_by_severity(db: Session, severity_level: str) -> List[FootConditionPreset]:
        """Get presets by severity level."""
        return db.query(FootConditionPreset).filter(
            FootConditionPreset.severity_level == severity_level
        ).order_by(FootConditionPreset.condition_name).all()

    @staticmethod
    def delete(db: Session, preset_id: str) -> bool:
        """Delete preset."""
        preset = db.query(FootConditionPreset).filter(FootConditionPreset.id == preset_id).first()
        if preset:
            db.delete(preset)
            db.commit()
            return True
        return False
