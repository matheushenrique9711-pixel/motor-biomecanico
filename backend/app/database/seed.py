"""
Database seeding script for development and testing.
Populates the database with sample clinical cases and patients.
"""

from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.database.models import (
    Patient, ClinicalCase, CaseStatusEnum, CaseAnalysis,
    AdjustmentHistory, CaseNotes
)


def seed_test_patients(db: Session) -> list[Patient]:
    """Create test patients for development."""
    patients = [
        Patient(
            patient_id="PAT-001",
            name="João Silva",
            age=45,
            gender="M",
            main_complaint="Dor nos pés durante caminhada",
            medical_history="Sem histórico relevante",
            current_medications="Dipirona conforme necessário",
            phone="(11) 98765-4321",
            email="joao.silva@email.com"
        ),
        Patient(
            patient_id="PAT-002",
            name="Maria Santos",
            age=32,
            gender="F",
            main_complaint="Fascite plantar crônica",
            medical_history="Diabetes tipo 2 (controlada)",
            current_medications="Metformina 1000mg",
            phone="(11) 99876-5432",
            email="maria.santos@email.com"
        ),
        Patient(
            patient_id="PAT-003",
            name="Carlos Oliveira",
            age=58,
            gender="M",
            main_complaint="Artrose no pé esquerdo",
            medical_history="Hipertensão arterial",
            current_medications="Lisinopril 10mg",
            phone="(11) 97654-3210",
            email="carlos.oliveira@email.com"
        ),
    ]

    for patient in patients:
        existing = db.query(Patient).filter(Patient.patient_id == patient.patient_id).first()
        if not existing:
            db.add(patient)

    db.commit()
    return db.query(Patient).all()


def seed_test_cases(db: Session) -> list[ClinicalCase]:
    """Create test clinical cases."""
    patients = db.query(Patient).all()
    if not patients:
        patients = seed_test_patients(db)

    cases = [
        ClinicalCase(
            case_id="CASE-001",
            patient_id=patients[0].id,
            status=CaseStatusEnum.ANALYZED,
            biomechanical_profile={
                "foot_length": 265.0,
                "arch_length_midfoot": 130.0,
                "forefoot_width": 98.0,
                "midfoot_width": 88.0,
                "hindfoot_width": 68.0,
                "arch_height_at_50pct": 22.0,
                "arch_height_at_midfoot": 24.0,
                "arch_index": 0.18,
                "foot_type": "normal",
                "pronation_level": "neutral"
            },
            analysis_confidence=0.92,
            analysis_notes="Análise bem sucedida. Pé normal com pronação neutra.",
            primary_condition="Pé Plano Leve",
            secondary_conditions=["Fadiga muscular"],
            suggestions=[],
        ),
        ClinicalCase(
            case_id="CASE-002",
            patient_id=patients[1].id,
            status=CaseStatusEnum.SUGGESTIONS_GENERATED,
            biomechanical_profile={
                "foot_length": 235.0,
                "arch_length_midfoot": 110.0,
                "forefoot_width": 88.0,
                "midfoot_width": 78.0,
                "hindfoot_width": 62.0,
                "arch_height_at_50pct": 18.0,
                "arch_height_at_midfoot": 20.0,
                "arch_index": 0.17,
                "foot_type": "flat",
                "pronation_level": "over"
            },
            analysis_confidence=0.88,
            analysis_notes="Pronação excessiva detectada. Compatível com fascite plantar.",
            primary_condition="Fascite Plantar",
            secondary_conditions=["Pé Plano", "Pronação Excessiva"],
            suggestions=[
                {
                    "condition": "Fascite Plantar",
                    "recommendation": "Aumentar suporte do arco medial",
                    "parameter_adjustments": [
                        {
                            "parameter": "arch_height_medial",
                            "current_value": 18.0,
                            "suggested_value": 24.0,
                            "unit": "mm"
                        }
                    ],
                    "severity_level": "moderado"
                }
            ],
        ),
        ClinicalCase(
            case_id="CASE-003",
            patient_id=patients[2].id,
            status=CaseStatusEnum.ADJUSTMENTS_CONFIRMED,
            biomechanical_profile={
                "foot_length": 275.0,
                "arch_length_midfoot": 135.0,
                "forefoot_width": 102.0,
                "midfoot_width": 92.0,
                "hindfoot_width": 72.0,
                "arch_height_at_50pct": 19.0,
                "arch_height_at_midfoot": 21.0,
                "arch_index": 0.16,
                "foot_type": "normal",
                "pronation_level": "neutral"
            },
            analysis_confidence=0.85,
            analysis_notes="Artrose detectada. Recomenda-se suporte estruturado.",
            primary_condition="Artrose de Tornozelo",
            secondary_conditions=["Idade avançada"],
            suggestions=[],
            insole_parameters={
                "arch_height_medial": 20.0,
                "arch_height_lateral": 18.0,
                "heel_height": 12.0,
                "metatarsal_support": True,
                "material": "EVA",
                "thickness": 8.0
            },
            parameters_modified_by_clinician=True,
            clinician_id="CLI-001",
            clinician_notes="Ajustado para melhor distribuição de carga e redução de dor",
        ),
    ]

    for case in cases:
        existing = db.query(ClinicalCase).filter(ClinicalCase.case_id == case.case_id).first()
        if not existing:
            db.add(case)

    db.commit()
    return db.query(ClinicalCase).all()


def seed_adjustment_history(db: Session) -> None:
    """Create adjustment history records."""
    cases = db.query(ClinicalCase).filter(
        ClinicalCase.case_id == "CASE-003"
    ).all()

    if not cases:
        return

    case = cases[0]

    # Check if history already exists
    existing = db.query(AdjustmentHistory).filter(
        AdjustmentHistory.case_id == case.id
    ).first()

    if not existing:
        adjustment = AdjustmentHistory(
            case_id=case.id,
            adjustment_type="clinician",
            previous_parameters={
                "arch_height_medial": 18.0,
                "arch_height_lateral": 16.0,
                "heel_height": 10.0,
            },
            new_parameters={
                "arch_height_medial": 20.0,
                "arch_height_lateral": 18.0,
                "heel_height": 12.0,
            },
            modified_by="CLI-001",
            reason="Ajuste clínico para melhor suporte e conforto"
        )
        db.add(adjustment)
        db.commit()


def seed_case_notes(db: Session) -> None:
    """Create sample case notes."""
    cases = db.query(ClinicalCase).all()

    for case in cases:
        existing = db.query(CaseNotes).filter(
            CaseNotes.case_id == case.id
        ).first()

        if not existing:
            note = CaseNotes(
                case_id=case.id,
                note_type="observation",
                content="Caso criado para teste e desenvolvimento",
                author_id="SYSTEM"
            )
            db.add(note)

    db.commit()


def seed_database(db: Session) -> dict:
    """
    Seed the entire database with test data.
    Returns statistics about created records.
    """
    try:
        # Check if database already seeded
        existing_patients = db.query(Patient).count()
        if existing_patients > 0:
            return {
                "status": "already_seeded",
                "message": f"Database already contains {existing_patients} patients"
            }

        # Seed in order
        seed_test_patients(db)
        seed_test_cases(db)
        seed_adjustment_history(db)
        seed_case_notes(db)

        # Get statistics
        patient_count = db.query(Patient).count()
        case_count = db.query(ClinicalCase).count()
        adjustment_count = db.query(AdjustmentHistory).count()
        note_count = db.query(CaseNotes).count()

        return {
            "status": "success",
            "message": "Database seeded successfully",
            "statistics": {
                "patients": patient_count,
                "cases": case_count,
                "adjustments": adjustment_count,
                "notes": note_count
            }
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": f"Seeding failed: {str(e)}"
        }
