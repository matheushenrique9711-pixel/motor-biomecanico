# Motor Biomecânico - Database Integration Guide

Quick reference for developers using the database layer.

## Quick Start

### Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Update database password if needed
export DB_PASSWORD=your_secure_password
```

### Starting Services

```bash
# With database (recommended)
docker-compose up -d

# Check database health
curl http://localhost:8000/health
```

## Using the Database Layer

### Import Required Classes

```python
from sqlalchemy.orm import Session
from fastapi import Depends

from app.database import (
    get_db,                          # FastAPI dependency
    ClinicalCaseRepository,          # Data access layer
    PatientRepository,               # Patient data
    AdjustmentHistoryRepository,     # Audit trail
)
from app.database.models import (
    ClinicalCase,                    # ORM model
    Patient,                         # Patient model
    CaseStatusEnum,                  # Case status enum
)
```

### Create FastAPI Route with Database

```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/cases/{case_id}")
async def get_case(
    case_id: str,
    db: Session = Depends(get_db)  # Inject database session
):
    """Get a clinical case by ID."""
    case = ClinicalCaseRepository.get_by_case_id(db, case_id)
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return case
```

## Common Database Operations

### Create Operations

```python
# Create a new patient
from app.database import PatientRepository

patient = PatientRepository.create(
    db=db,
    patient_id="PAT-001",
    name="João Silva",
    age=45,
    gender="M",
    main_complaint="Dor nos pés",
    medical_history="Sem histórico relevante",
    phone="(11) 98765-4321",
    email="joao@email.com"
)

# Create a clinical case
from app.database import ClinicalCaseRepository

case = ClinicalCaseRepository.create(
    db=db,
    case_id="CASE-001",
    patient_id=patient.id  # Use patient's UUID
)
```

### Read Operations

```python
# Get case by case_id
case = ClinicalCaseRepository.get_by_case_id(db, "CASE-001")

# Get all cases for a patient
cases = ClinicalCaseRepository.list_by_patient(db, patient_id)

# Get cases by status
active_cases = ClinicalCaseRepository.list_by_status(
    db, 
    CaseStatusEnum.ANALYZED,
    limit=50,
    offset=0
)

# List all cases
all_cases = ClinicalCaseRepository.list_all(db, limit=50, offset=0)
```

### Update Operations

```python
# Update case status
ClinicalCaseRepository.update_status(
    db=db,
    case_id="CASE-001",
    status=CaseStatusEnum.ANALYZED
)

# Add biomechanical analysis
ClinicalCaseRepository.update_biomechanical_analysis(
    db=db,
    case_id="CASE-001",
    biomechanical_profile={
        "foot_length": 265.0,
        "arch_index": 0.18,
        "foot_type": "normal"
    },
    analysis_confidence=0.92,
    analysis_notes="Análise realizada com sucesso"
)

# Update suggestions
ClinicalCaseRepository.update_suggestions(
    db=db,
    case_id="CASE-001",
    primary_condition="Pé Plano Leve",
    secondary_conditions=["Fadiga muscular"],
    suggestions=[
        {
            "condition": "Pé Plano Leve",
            "recommendation": "Aumentar suporte do arco",
            "severity_level": "leve"
        }
    ]
)

# Update insole parameters
ClinicalCaseRepository.update_insole_parameters(
    db=db,
    case_id="CASE-001",
    insole_parameters={
        "arch_height_medial": 20.0,
        "heel_height": 12.0,
        "material": "EVA"
    },
    modified_by_clinician=True,
    clinician_id="CLI-001",
    clinician_notes="Ajustado para melhor conforto"
)

# Register STL export
ClinicalCaseRepository.register_stl_export(
    db=db,
    case_id="CASE-001",
    stl_file_path="/tmp/stl_exports/CASE-001.stl",
    geometry_notes="Geometria parametrizada com sucesso"
)

# Add feedback
ClinicalCaseRepository.add_feedback(
    db=db,
    case_id="CASE-001",
    clinical_feedback="Ótima aceitação pelo paciente",
    patient_feedback="Muito confortável",
    quality_score=0.95
)
```

### Delete Operations

```python
# Delete a case (cascades to related records)
ClinicalCaseRepository.delete(db, "CASE-001")

# Delete a patient (cascades to all cases)
PatientRepository.delete(db, patient_id)
```

## Audit Trail & History

```python
# Create adjustment history record
from app.database import AdjustmentHistoryRepository

AdjustmentHistoryRepository.create(
    db=db,
    case_id=case.id,
    adjustment_type="clinician",
    previous_parameters={"arch_height_medial": 18.0},
    new_parameters={"arch_height_medial": 20.0},
    modified_by="CLI-001",
    reason="Ajuste clínico para melhor suporte"
)

# Get adjustment history for a case
history = AdjustmentHistoryRepository.get_case_history(db, case.id)
for adjustment in history:
    print(f"{adjustment.modified_by} adjusted on {adjustment.created_at}")
```

## Adding Clinical Notes

```python
from app.database import CaseNotesRepository

# Add observation note
CaseNotesRepository.create(
    db=db,
    case_id=case.id,
    note_type="observation",
    content="Paciente relatou dor no arco após 2 horas de uso",
    author_id="CLI-001"
)

# Get all notes for a case
notes = CaseNotesRepository.get_case_notes(db, case.id)
for note in notes:
    print(f"[{note.note_type}] {note.content} - by {note.author_id}")
```

## Managing File Attachments

```python
from app.database import CaseFileRepository

# Add file to case
file_record = CaseFileRepository.create(
    db=db,
    case_id=case.id,
    file_name="scan_image.jpg",
    file_path="/uploads/CASE-001/scan_image.jpg",
    file_type="image",
    file_size=2048576,  # 2MB
    uploaded_by="CLI-001",
    description="Imagem do pé esquerdo"
)

# Get all files for a case
files = CaseFileRepository.get_case_files(db, case.id)
for file in files:
    print(f"{file.file_name} ({file.file_type}) - {file.file_size} bytes")

# Delete a file
CaseFileRepository.delete(db, file_id)
```

## Transaction Management

### Safe Operations with Rollback

```python
from sqlalchemy.exc import SQLAlchemyError

async def create_case_with_analysis(
    db: Session,
    patient_info: dict,
    biomechanical_data: dict
):
    """Create case and analysis in a single transaction."""
    try:
        # Create patient
        patient = PatientRepository.create(db, **patient_info)
        
        # Create case
        case = ClinicalCaseRepository.create(
            db=db,
            case_id=f"CASE-{patient.id}",
            patient_id=patient.id
        )
        
        # Add analysis
        analysis = CaseAnalysisRepository.create(
            db=db,
            case_id=case.id,
            **biomechanical_data
        )
        
        # All succeeded - changes are committed
        return case
        
    except SQLAlchemyError as e:
        db.rollback()  # Undo all changes
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
```

## Query Patterns

### Filter and Count

```python
from sqlalchemy import func

# Count cases by status
analyzed_count = db.query(ClinicalCase).filter(
    ClinicalCase.status == CaseStatusEnum.ANALYZED
).count()

# Get recent cases
recent_cases = db.query(ClinicalCase).order_by(
    ClinicalCase.created_at.desc()
).limit(10).all()
```

### JSONB Queries

```python
from sqlalchemy import text

# Query JSONB data (biomechanical_profile)
cases_with_low_arch = db.query(ClinicalCase).filter(
    ClinicalCase.biomechanical_profile['arch_index'].astext.cast(float) < 0.15
).all()

# Using raw SQL for complex JSONB queries
result = db.execute(text("""
    SELECT * FROM clinical_cases 
    WHERE biomechanical_profile->>'foot_type' = 'flat'
    ORDER BY created_at DESC
    LIMIT 20
"""))
cases = result.fetchall()
```

## Database Health & Info

```python
from app.database import get_database_info

# Get current database statistics
info = get_database_info()

if info['status'] == 'healthy':
    stats = info['tables']
    print(f"Patients: {stats['patients']}")
    print(f"Cases: {stats['clinical_cases']}")
    print(f"Adjustments: {stats['adjustment_history']}")
```

## Error Handling

```python
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException

@router.post("/cases/")
async def create_case(case_data: dict, db: Session = Depends(get_db)):
    try:
        case = ClinicalCaseRepository.create(
            db=db,
            case_id=case_data['case_id'],
            patient_id=case_data['patient_id']
        )
        return case
        
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Case already exists")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")
```

## Pagination

```python
# Simple pagination
def list_cases_paginated(db: Session, page: int = 1, page_size: int = 20):
    skip = (page - 1) * page_size
    cases = ClinicalCaseRepository.list_all(
        db=db,
        limit=page_size,
        offset=skip
    )
    
    total = db.query(ClinicalCase).count()
    
    return {
        "items": cases,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }
```

## Bulk Operations

```python
# Bulk create
patients_data = [
    {"patient_id": "PAT-001", "name": "João", "age": 45, "gender": "M", "main_complaint": "Dor"},
    {"patient_id": "PAT-002", "name": "Maria", "age": 32, "gender": "F", "main_complaint": "Fascite"},
]

for patient_data in patients_data:
    PatientRepository.create(db, **patient_data)

db.commit()  # Commit all at once
```

## Troubleshooting

### Sessions & Connections

```python
# Session is closed
# Error: "Cannot operate on a closed database connection"
# Solution: Ensure get_db() dependency is used

@router.get("/cases/")
async def list_cases(db: Session = Depends(get_db)):  # ✓ Correct
    return ClinicalCaseRepository.list_all(db)

# ✗ Wrong - creates its own session that closes
db = SessionLocal()
cases = ClinicalCaseRepository.list_all(db)
db.close()
```

### Data Type Mismatches

```python
# Always use correct types
case = ClinicalCaseRepository.update_biomechanical_analysis(
    db=db,
    case_id="CASE-001",  # String ✓
    biomechanical_profile={...},  # Dict ✓
    analysis_confidence=0.92  # Float ✓
)

# ✗ Wrong
case = ClinicalCaseRepository.update_biomechanical_analysis(
    db=db,
    case_id=123,  # Should be string
    biomechanical_profile="...",  # Should be dict
    analysis_confidence="0.92"  # Should be float
)
```

### Relationship Issues

```python
# Always ensure relationships are properly loaded
case = ClinicalCaseRepository.get_by_case_id(db, "CASE-001")

# Access related patient
patient = case.patient  # ✓ Works - lazy loaded

# After session is closed
# case.patient  # ✗ Error - relationship not loaded

# Solution: Load relationships with query
from sqlalchemy.orm import joinedload
case = db.query(ClinicalCase).options(
    joinedload(ClinicalCase.patient)
).filter(ClinicalCase.case_id == "CASE-001").first()
```

## Best Practices

1. **Always use `Depends(get_db)`** for FastAPI routes
2. **Use repositories** for data access (never query ORM directly in routes)
3. **Handle exceptions** with proper HTTP status codes
4. **Paginate large results** to avoid memory issues
5. **Use JSONB wisely** for semi-structured data
6. **Keep transactions small** for better concurrency
7. **Index queryable columns** for performance
8. **Log database operations** in production
9. **Use environment variables** for credentials
10. **Test database operations** before deployment

## Example: Complete Case Workflow

```python
@router.post("/cases/{patient_id}/workflow")
async def complete_case_workflow(
    patient_id: str,
    request: WorkflowRequest,
    db: Session = Depends(get_db)
):
    """Complete workflow from analysis to geometry export."""
    
    # Get or create patient
    patient = PatientRepository.get_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Create case
    case = ClinicalCaseRepository.create(
        db=db,
        case_id=f"CASE-{uuid.uuid4()}",
        patient_id=patient.id
    )
    
    # Step 1: Add analysis
    ClinicalCaseRepository.update_biomechanical_analysis(
        db=db,
        case_id=case.case_id,
        biomechanical_profile=request.biomechanical_profile,
        analysis_confidence=request.confidence
    )
    
    # Step 2: Generate suggestions
    ClinicalCaseRepository.update_suggestions(
        db=db,
        case_id=case.case_id,
        primary_condition=request.condition,
        suggestions=request.suggestions
    )
    
    # Step 3: Apply adjustments
    ClinicalCaseRepository.update_insole_parameters(
        db=db,
        case_id=case.case_id,
        insole_parameters=request.insole_params,
        modified_by_clinician=request.clinician_modified,
        clinician_id=request.clinician_id
    )
    
    # Step 4: Register geometry export
    ClinicalCaseRepository.register_stl_export(
        db=db,
        case_id=case.case_id,
        stl_file_path=request.stl_path
    )
    
    # Add clinical note
    CaseNotesRepository.create(
        db=db,
        case_id=case.id,
        note_type="observation",
        content=request.clinician_notes,
        author_id=request.clinician_id
    )
    
    return case
```

## More Information

- See `PHASE_4_DATABASE_COMPLETE.md` for full Phase 4 documentation
- See `DOCKER_SETUP.md` for Docker/container information
- Check `alembic/` directory for migration management
- Review `app/database/models.py` for ORM schema

---

**Motor Biomecânico - Database Guide v1.0**  
