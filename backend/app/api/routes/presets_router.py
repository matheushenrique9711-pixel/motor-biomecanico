"""
API routes for foot condition presets.
Provides endpoints to retrieve and manage pre-configured foot condition templates.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, PresetRepository
from app.database.models import FootConditionPreset

router = APIRouter(prefix="/presets", tags=["Presets"])


@router.get("/", response_model=List[dict])
def get_all_presets(db: Session = Depends(get_db)):
    """
    Get all foot condition presets.

    Returns a list of all pre-configured foot condition templates with
    recommended parameters for quick application to cases.
    """
    try:
        presets = PresetRepository.get_all(db)
        result = []
        for preset in presets:
            result.append({
                "id": str(preset.id),
                "condition_name": preset.condition_name,
                "description": preset.description,
                "severity_level": preset.severity_level,
                "clinical_indicators": preset.clinical_indicators,
                "common_complaints": preset.common_complaints,
                "recommended_parameters": preset.recommended_parameters,
                "arch_support_level": preset.arch_support_level,
                "heel_height_mm": preset.heel_height_mm,
                "material_recommendation": preset.material_recommendation,
                "illustration_path": preset.illustration_path,
                "reference_image_url": preset.reference_image_url,
                "created_at": preset.created_at.isoformat() if preset.created_at else None
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch presets: {str(e)}")


@router.get("/{condition_name}", response_model=dict)
def get_preset_by_name(condition_name: str, db: Session = Depends(get_db)):
    """
    Get a specific preset by condition name.

    Parameters:
    - condition_name: Name of the foot condition (e.g., "Pé Plano Leve")

    Returns the preset details including recommended insole parameters.
    """
    try:
        preset = PresetRepository.get_by_name(db, condition_name)
        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset '{condition_name}' not found")

        return {
            "id": str(preset.id),
            "condition_name": preset.condition_name,
            "description": preset.description,
            "severity_level": preset.severity_level,
            "clinical_indicators": preset.clinical_indicators,
            "common_complaints": preset.common_complaints,
            "recommended_parameters": preset.recommended_parameters,
            "arch_support_level": preset.arch_support_level,
            "heel_height_mm": preset.heel_height_mm,
            "material_recommendation": preset.material_recommendation,
            "illustration_path": preset.illustration_path,
            "reference_image_url": preset.reference_image_url,
            "created_at": preset.created_at.isoformat() if preset.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching preset: {str(e)}")


@router.get("/severity/{severity_level}", response_model=List[dict])
def get_presets_by_severity(severity_level: str, db: Session = Depends(get_db)):
    """
    Get presets by severity level.

    Parameters:
    - severity_level: "leve", "moderada", or "severa"

    Returns all presets matching the severity level.
    """
    valid_severities = ["leve", "moderada", "severa", "máximo"]
    if severity_level not in valid_severities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid severity level. Must be one of: {', '.join(valid_severities)}"
        )

    try:
        presets = PresetRepository.get_by_severity(db, severity_level)
        result = []
        for preset in presets:
            result.append({
                "id": str(preset.id),
                "condition_name": preset.condition_name,
                "description": preset.description,
                "severity_level": preset.severity_level,
                "clinical_indicators": preset.clinical_indicators,
                "common_complaints": preset.common_complaints,
                "recommended_parameters": preset.recommended_parameters,
                "arch_support_level": preset.arch_support_level,
                "heel_height_mm": preset.heel_height_mm,
                "material_recommendation": preset.material_recommendation,
                "created_at": preset.created_at.isoformat() if preset.created_at else None
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching presets: {str(e)}")


@router.post("/apply/{case_id}", response_model=dict)
def apply_preset_to_case(
    case_id: str,
    condition_name: str,
    db: Session = Depends(get_db)
):
    """
    Apply a preset's recommended parameters to a clinical case.

    Parameters:
    - case_id: ID of the case to apply preset to
    - condition_name: Name of the preset condition

    Returns the case with updated parameters.
    """
    from app.database import ClinicalCaseRepository

    try:
        # Get preset
        preset = PresetRepository.get_by_name(db, condition_name)
        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset '{condition_name}' not found")

        # Get case
        case = ClinicalCaseRepository.get_by_case_id(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")

        # Apply preset parameters
        case.insole_parameters = preset.recommended_parameters
        case.primary_condition = condition_name

        db.commit()
        db.refresh(case)

        return {
            "case_id": case.case_id,
            "message": f"Preset '{condition_name}' applied successfully",
            "applied_parameters": preset.recommended_parameters,
            "arch_support_level": preset.arch_support_level,
            "heel_height_mm": preset.heel_height_mm,
            "material_recommendation": preset.material_recommendation
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error applying preset: {str(e)}")


@router.get("/", tags=["Info"])
def preset_info():
    """
    Get information about available presets.

    Returns summary information about the preset system.
    """
    return {
        "message": "Use GET /presets/ to get all presets",
        "severity_levels": ["leve", "moderada", "severa"],
        "endpoints": {
            "GET /presets/": "Get all presets",
            "GET /presets/{condition_name}": "Get specific preset",
            "GET /presets/severity/{level}": "Get presets by severity",
            "POST /presets/apply/{case_id}": "Apply preset to case"
        }
    }
