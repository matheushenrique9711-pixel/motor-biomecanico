"""
Endpoints de API para gerenciamento de casos clínicos.
Fornece os endpoints principais para análise, sugestões, aplicação de ajustes e exportação.
Integrado com camada de banco de dados PostgreSQL.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import io
import uuid

from app.models import (
    ClinicalCase,
    CaseStatus,
    PatientInfo,
    BiomechanicalFootProfile,
    LoadDistribution,
    InsoleParameterSet,
    CaseAnalysisResult,
    CaseExportRequest,
    CaseFeedbackRequest,
)
from app.services import SuggestionEngine, GeometryGenerator
from app.database import (
    get_db,
    PatientRepository,
    ClinicalCaseRepository,
    CaseNotesRepository,
    AdjustmentHistoryRepository,
)
from app.database.models import CaseStatusEnum

# Inicializa router e serviços
router = APIRouter(prefix="/cases", tags=["cases"])

# Serviços (injetados conforme necessário)
_suggestion_engine = SuggestionEngine()
_geometry_generator = GeometryGenerator()


# ========== CRIAÇÃO DE CASOS ==========

@router.post("/", response_model=dict, summary="Criar novo caso")
async def create_case(patient_info: PatientInfo, db: Session = Depends(get_db)):
    """
    Cria um novo caso clínico para um paciente.

    Args:
        patient_info: Informações do paciente (nome, age, queixa principal, etc)
        db: Sessão de banco de dados

    Returns:
        ClinicalCase criado
    """
    try:
        # Cria paciente
        patient = PatientRepository.create(
            db=db,
            patient_id=str(uuid.uuid4()),
            name=patient_info.name,
            age=patient_info.age,
            gender=patient_info.gender,
            main_complaint=patient_info.main_complaint,
            medical_history=patient_info.medical_history or "",
            phone=patient_info.phone or "",
            email=patient_info.email or "",
        )

        # Cria caso clínico
        case_id = f"CASE-{uuid.uuid4()}"
        case = ClinicalCaseRepository.create(
            db=db,
            case_id=case_id,
            patient_id=patient.id,
        )

        db.commit()

        return {
            "case_id": case.case_id,
            "patient_id": patient.patient_id,
            "patient_name": patient.name,
            "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "id": str(case.id),
        }

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Paciente ou caso já existe")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


# ========== ANÁLISE DE CASOS ==========

@router.post("/{case_id}/analyze", response_model=dict, summary="Analisar pé")
async def analyze_case(
    case_id: str,
    biomechanical_profile: BiomechanicalFootProfile,
    db: Session = Depends(get_db),
):
    """
    Registra análise biomecânica para um caso.
    Em produção, aceitaria arquivo de imagem e executaria extração de parâmetros.

    Args:
        case_id: ID do caso
        biomechanical_profile: Perfil biomecânico extraído
        db: Sessão de banco de dados

    Returns:
        Resultado da análise com perfil e detecções
    """
    try:
        # Busca caso
        case = ClinicalCaseRepository.get_by_case_id(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} não encontrado")

        # Valida o perfil
        try:
            profile = BiomechanicalFootProfile(**biomechanical_profile.dict())
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Perfil inválido: {str(e)}")

        # Atualiza caso com análise
        analysis_confidence = 0.85  # Simplificado - em produção viria do detector
        biomechanical_dict = profile.dict()

        case = ClinicalCaseRepository.update_biomechanical_analysis(
            db=db,
            case_id=case_id,
            biomechanical_profile=biomechanical_dict,
            analysis_confidence=analysis_confidence,
            analysis_notes="Análise registrada via API",
        )

        db.commit()

        # Retorna resultado
        return {
            "case_id": case_id,
            "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
            "biomechanical_profile": case.biomechanical_profile,
            "conditions_detected": [case.primary_condition] if case.primary_condition else [],
            "suggestions": [],
            "analysis_confidence": case.analysis_confidence or 0.0,
            "next_steps": [
                "Revisar análise",
                "Gerar sugestões clínicas",
                "Confirmar ajustes",
            ],
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


# ========== SUGESTÕES CLÍNICAS ==========

@router.post("/{case_id}/suggestions", response_model=dict, summary="Gerar sugestões")
async def generate_suggestions(case_id: str, db: Session = Depends(get_db)):
    """
    Gera sugestões clínicas para um caso baseado na análise biomecânica.

    Args:
        case_id: ID do caso
        db: Sessão de banco de dados

    Returns:
        Dict com sugestões geradas
    """
    try:
        # Busca caso
        case = ClinicalCaseRepository.get_by_case_id(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} não encontrado")

        if not case.biomechanical_profile:
            raise HTTPException(
                status_code=400,
                detail="Caso não possui análise biomecânica. Execute /analyze primeiro.",
            )

        # Reconstrói perfil do dict
        profile_dict = case.biomechanical_profile
        load_dist_data = profile_dict.get("load_distribution", {})

        profile = BiomechanicalFootProfile(
            foot_length=profile_dict.get("foot_length", 250.0),
            arch_length_midfoot=profile_dict.get("arch_length_midfoot", 120.0),
            forefoot_width=profile_dict.get("forefoot_width", 95.0),
            midfoot_width=profile_dict.get("midfoot_width", 85.0),
            hindfoot_width=profile_dict.get("hindfoot_width", 65.0),
            arch_height_at_50pct=profile_dict.get("arch_height_at_50pct", 20.0),
            arch_height_at_midfoot=profile_dict.get("arch_height_at_midfoot", 22.0),
            arch_index=profile_dict.get("arch_index", 0.16),
            hallux_valgus_angle=profile_dict.get("hallux_valgus_angle", 0.0),
            intermetatarsal_angle=profile_dict.get("intermetatarsal_angle", 0.0),
            subtalar_inversion_angle=profile_dict.get("subtalar_inversion_angle", 0.0),
            tibial_torsion_asymmetry=profile_dict.get("tibial_torsion_asymmetry", 0.0),
            load_distribution=LoadDistribution(**load_dist_data) if load_dist_data else LoadDistribution(
                hallux_zone=0.15, medial_metatarsal=0.20, central_metatarsal=0.25,
                lateral_metatarsal=0.15, heel_zone=0.25
            ),
            left_right_asymmetry=profile_dict.get("left_right_asymmetry", 0.0),
            scan_quality=profile_dict.get("scan_quality", 0.95),
        )

        # Gera sugestões
        suggestions = _suggestion_engine.generate_suggestions(profile)

        # Atualiza caso com sugestões
        suggestions_data = [s.dict() for s in suggestions]
        primary_condition = suggestions_data[0].get("condition", "Desconhecida") if suggestions_data else None

        case = ClinicalCaseRepository.update_suggestions(
            db=db,
            case_id=case_id,
            primary_condition=primary_condition,
            secondary_conditions=[],
            suggestions=suggestions_data,
        )

        db.commit()

        return {
            "case_id": case_id,
            "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
            "suggestions_count": len(suggestions),
            "suggestions": suggestions_data,
            "primary_condition": case.primary_condition,
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


@router.post("/{case_id}/confirm-suggestions", response_model=dict, summary="Confirmar sugestões")
async def confirm_suggestions(
    case_id: str,
    clinician_id: str,
    clinician_notes: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Marca sugestões como confirmadas pelo clínico.

    Args:
        case_id: ID do caso
        clinician_id: ID do clínico responsável
        clinician_notes: Notas do clínico
        db: Sessão de banco de dados

    Returns:
        Caso atualizado
    """
    try:
        # Busca caso
        case = ClinicalCaseRepository.get_by_case_id(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} não encontrado")

        # Atualiza status para sugestões revisadas
        case = ClinicalCaseRepository.update_status(
            db=db,
            case_id=case_id,
            status=CaseStatusEnum.SUGGESTIONS_REVIEWED,
        )

        # Adiciona nota clínica se fornecida
        if clinician_notes:
            CaseNotesRepository.create(
                db=db,
                case_id=case.id,
                note_type="clinician_review",
                content=clinician_notes,
                author_id=clinician_id,
            )

        db.commit()

        return {
            "case_id": case.case_id,
            "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
            "message": "Sugestões confirmadas com sucesso",
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


# ========== APLICAÇÃO DE AJUSTES ==========

@router.post("/{case_id}/apply-adjustments", response_model=dict, summary="Aplicar ajustes")
async def apply_adjustments(
    case_id: str,
    insole_parameters: InsoleParameterSet,
    modified_by_clinician: bool = False,
    clinician_id: Optional[str] = None,
    clinician_notes: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Aplica ajustes de parâmetros da palmilha ao caso.

    Args:
        case_id: ID do caso
        insole_parameters: Parâmetros finais da palmilha
        modified_by_clinician: Se foi modificado pelo clínico
        clinician_id: ID do clínico que fez os ajustes
        clinician_notes: Notas do clínico sobre os ajustes
        db: Sessão de banco de dados

    Returns:
        Caso atualizado com parâmetros aplicados
    """
    try:
        # Busca caso
        case = ClinicalCaseRepository.get_by_case_id(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} não encontrado")

        # Valida os parâmetros
        is_valid, warnings = insole_parameters.validate()

        if not is_valid and modified_by_clinician:
            # Se clinician confirmou, segue mesmo com warnings
            pass

        # Registra parâmetros no banco
        parameters_dict = insole_parameters.dict()
        case = ClinicalCaseRepository.update_insole_parameters(
            db=db,
            case_id=case_id,
            insole_parameters=parameters_dict,
            modified_by_clinician=modified_by_clinician,
            clinician_id=clinician_id or "CLI-001",
            clinician_notes=clinician_notes or "Parâmetros aplicados via API",
        )

        # Registra histórico de ajustes se foi modificado
        if modified_by_clinician and clinician_id:
            AdjustmentHistoryRepository.create(
                db=db,
                case_id=case.id,
                adjustment_type="clinician",
                previous_parameters={},
                new_parameters=parameters_dict,
                modified_by=clinician_id,
                reason=clinician_notes or "Ajuste clínico aplicado",
            )

        # Atualiza status para parâmetros confirmados
        case = ClinicalCaseRepository.update_status(
            db=db,
            case_id=case_id,
            status=CaseStatusEnum.ADJUSTMENTS_CONFIRMED,
        )

        db.commit()

        return {
            "case_id": case.case_id,
            "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
            "insole_parameters": parameters_dict,
            "modified_by_clinician": modified_by_clinician,
            "message": "Parâmetros aplicados com sucesso",
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


# ========== GEOMETRIA E EXPORTAÇÃO ==========

@router.post("/{case_id}/generate-geometry", response_model=dict, summary="Gerar geometria 3D")
async def generate_geometry(case_id: str, db: Session = Depends(get_db)):
    """
    Gera geometria 3D parametrizada para palmilha ortopédica usando CadQuery.

    Args:
        case_id: ID do caso
        db: Sessão de banco de dados

    Returns:
        Info da geometria gerada
    """
    try:
        # Busca caso
        case = ClinicalCaseRepository.get_by_case_id(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} não encontrado")

        if not case.biomechanical_profile:
            raise HTTPException(
                status_code=400,
                detail="Caso não possui análise biomecânica. Execute /analyze primeiro.",
            )

        if not case.primary_condition:
            raise HTTPException(
                status_code=400,
                detail="Nenhuma condição detectada. Execute /suggestions primeiro.",
            )

        # Extrai parâmetros do caso
        profile = case.biomechanical_profile
        foot_length = profile.get('foot_length', 250.0)
        foot_width = profile.get('forefoot_width', 95.0)
        arch_index = profile.get('arch_index', 0.16)

        # Gera geometria usando os parâmetros do caso
        geometry_result = _geometry_generator.generate_insole_geometry(
            case_id=case_id,
            foot_length=foot_length,
            foot_width=foot_width,
            arch_index=arch_index,
            condition_type=case.primary_condition,
            parameters=case.insole_parameters or {'arch_height_medial': 6.0},
        )

        if geometry_result['success']:
            # Registra exportação no banco
            case = ClinicalCaseRepository.register_stl_export(
                db=db,
                case_id=case_id,
                stl_file_path=geometry_result['stl_path'],
                geometry_notes=f"Geometria parametrizada para condição: {geometry_result['condition']}",
            )

            # Atualiza status para geometria gerada
            case = ClinicalCaseRepository.update_status(
                db=db,
                case_id=case_id,
                status=CaseStatusEnum.GEOMETRY_GENERATED,
            )

            db.commit()

            return {
                "case_id": case_id,
                "success": True,
                "stl_file_path": geometry_result['stl_path'],
                "condition": geometry_result['condition'],
                "arch_index": geometry_result['arch_index'],
                "dimensions": geometry_result['dimensions'],
                "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
            }
        else:
            raise HTTPException(status_code=500, detail=geometry_result.get('error', 'Erro desconhecido'))

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar geometria: {str(e)}")


@router.post("/{case_id}/export-stl", response_model=dict, summary="Exportar STL")
async def export_stl(
    case_id: str,
    export_request: CaseExportRequest = None,
    db: Session = Depends(get_db),
):
    """
    Exporta arquivo STL gerado anteriormente.

    Args:
        case_id: ID do caso
        export_request: Parâmetros de exportação (opcional)
        db: Sessão de banco de dados

    Returns:
        Info do arquivo STL
    """
    try:
        # Busca caso
        case = ClinicalCaseRepository.get_by_case_id(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} não encontrado")

        if not case.stl_file_path:
            raise HTTPException(
                status_code=400,
                detail="Nenhuma geometria gerada. Execute /generate-geometry primeiro.",
            )

        try:
            stl_bytes, filename = _geometry_generator.get_stl_file(case_id)

            # Atualiza status para exportado
            case = ClinicalCaseRepository.update_status(
                db=db,
                case_id=case_id,
                status=CaseStatusEnum.EXPORTED,
            )
            db.commit()

            return {
                "case_id": case_id,
                "filename": filename,
                "size_bytes": len(stl_bytes),
                "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
                "message": "STL pronto para download",
            }
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


# ========== CONSULTA E LISTAGEM ==========

@router.get("/{case_id}", response_model=dict, summary="Obter caso")
async def get_case(case_id: str, db: Session = Depends(get_db)):
    """
    Retorna um caso específico.

    Args:
        case_id: ID do caso
        db: Sessão de banco de dados

    Returns:
        ClinicalCase completo
    """
    try:
        case = ClinicalCaseRepository.get_by_case_id(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} não encontrado")

        return {
            "case_id": case.case_id,
            "patient_id": str(case.patient_id) if case.patient_id else None,
            "patient_name": case.patient.name if case.patient else None,
            "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
            "primary_condition": case.primary_condition,
            "secondary_conditions": case.secondary_conditions or [],
            "biomechanical_profile": case.biomechanical_profile,
            "suggestions": case.suggestions,
            "insole_parameters": case.insole_parameters,
            "stl_file_path": case.stl_file_path,
            "analysis_confidence": case.analysis_confidence,
            "created_at": case.created_at.isoformat() if case.created_at else None,
            "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


@router.get("/", response_model=dict, summary="Listar casos")
async def list_cases(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Lista casos com filtros opcionais.

    Args:
        status: Filtrar por status
        limit: Máximo de casos
        offset: Deslocamento para paginação
        db: Sessão de banco de dados

    Returns:
        Lista de casos
    """
    try:
        if status:
            # Converte string para enum se necessário
            try:
                status_enum = CaseStatusEnum[status.upper()]
                cases = ClinicalCaseRepository.list_by_status(
                    db=db,
                    status=status_enum,
                    limit=limit,
                    offset=offset,
                )
            except KeyError:
                raise HTTPException(status_code=400, detail=f"Status inválido: {status}")
        else:
            cases = ClinicalCaseRepository.list_all(db=db, limit=limit, offset=offset)

        # Converte para dicts
        cases_list = []
        for case in cases:
            cases_list.append({
                "case_id": case.case_id,
                "patient_name": case.patient.name if case.patient else None,
                "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
                "primary_condition": case.primary_condition,
                "analysis_confidence": case.analysis_confidence,
                "created_at": case.created_at.isoformat() if case.created_at else None,
            })

        return {
            "cases": cases_list,
            "total": len(cases_list),
            "limit": limit,
            "offset": offset,
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


@router.get("/statistics/summary", response_model=dict, summary="Estatísticas")
async def get_statistics(db: Session = Depends(get_db)):
    """
    Retorna estatísticas gerais dos casos.

    Returns:
        Dict com contagens por status, condição, confiança média, etc
    """
    try:
        # Busca todos os casos
        all_cases = ClinicalCaseRepository.list_all(db=db, limit=10000, offset=0)

        # Calcula estatísticas
        total_cases = len(all_cases)
        status_counts = {}
        condition_counts = {}
        confidences = []

        for case in all_cases:
            # Conta por status
            status_str = case.status.value if hasattr(case.status, 'value') else str(case.status)
            status_counts[status_str] = status_counts.get(status_str, 0) + 1

            # Conta por condição
            if case.primary_condition:
                condition_counts[case.primary_condition] = condition_counts.get(case.primary_condition, 0) + 1

            # Coleta confiança
            if case.analysis_confidence:
                confidences.append(case.analysis_confidence)

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return {
            "total_cases": total_cases,
            "status_breakdown": status_counts,
            "condition_breakdown": condition_counts,
            "average_confidence": round(avg_confidence, 3),
            "cases_with_confidence": len(confidences),
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


# ========== FEEDBACK ==========

@router.post("/{case_id}/feedback", response_model=dict, summary="Registrar feedback")
async def add_feedback(
    case_id: str,
    feedback_request: CaseFeedbackRequest,
    db: Session = Depends(get_db),
):
    """
    Registra feedback clínico e do paciente após uso da palmilha.
    Importante para aprendizado contínuo do sistema.

    Args:
        case_id: ID do caso
        feedback_request: Feedback clínico e do paciente
        db: Sessão de banco de dados

    Returns:
        Caso atualizado com feedback
    """
    try:
        # Busca caso
        case = ClinicalCaseRepository.get_by_case_id(db, case_id)
        if not case:
            raise HTTPException(status_code=404, detail=f"Caso {case_id} não encontrado")

        # Adiciona feedback clínico se fornecido
        if feedback_request.clinical_feedback:
            case = ClinicalCaseRepository.add_feedback(
                db=db,
                case_id=case_id,
                clinical_feedback=feedback_request.clinical_feedback,
                patient_feedback=None,
                quality_score=None,
            )

        # Adiciona feedback do paciente se fornecido
        if feedback_request.patient_feedback:
            case = ClinicalCaseRepository.add_feedback(
                db=db,
                case_id=case_id,
                clinical_feedback=None,
                patient_feedback=feedback_request.patient_feedback,
                quality_score=feedback_request.effectiveness_score or 0.0,
            )

        # Atualiza status para feedback coletado
        case = ClinicalCaseRepository.update_status(
            db=db,
            case_id=case_id,
            status=CaseStatusEnum.FEEDBACK_COLLECTED,
        )

        db.commit()

        return {
            "case_id": case.case_id,
            "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
            "clinical_feedback": case.clinical_feedback,
            "patient_feedback": case.patient_feedback,
            "message": "Feedback registrado com sucesso",
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


# ========== PACIENTES ==========

@router.get("/patient/{patient_id}/cases", response_model=dict, summary="Casos do paciente")
async def get_patient_cases(patient_id: str, db: Session = Depends(get_db)):
    """
    Retorna todos os casos de um paciente.

    Args:
        patient_id: ID do paciente
        db: Sessão de banco de dados

    Returns:
        Lista de casos do paciente
    """
    try:
        cases = ClinicalCaseRepository.list_by_patient(db=db, patient_id=patient_id)

        # Converte para dicts
        cases_list = []
        for case in cases:
            cases_list.append({
                "case_id": case.case_id,
                "status": case.status.value if hasattr(case.status, 'value') else str(case.status),
                "primary_condition": case.primary_condition,
                "analysis_confidence": case.analysis_confidence,
                "created_at": case.created_at.isoformat() if case.created_at else None,
            })

        return {
            "patient_id": patient_id,
            "total_cases": len(cases_list),
            "cases": cases_list,
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro de banco de dados: {str(e)}")


# ========== HEALTH CHECK ==========

@router.get("/health", response_model=dict, summary="Health check")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database status."""
    try:
        # Testa conexão com banco
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "motor-biomecanico-api",
        "database": db_status,
    }
