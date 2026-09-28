"""
Modelos para casos clínicos.
Estrutura que representa um caso completo desde análise até aplicação de ajustes.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class CaseStatus(str, Enum):
    """Estados possíveis de um caso clínico."""
    CREATED = "created"                          # Caso criado, aguardando análise
    SCANNING = "scanning"                        # Foto sendo processada
    ANALYZED = "analyzed"                        # Análise completa, perfil extraído
    SUGGESTIONS_GENERATED = "suggestions_generated"  # Sugestões geradas
    SUGGESTIONS_REVIEWED = "suggestions_reviewed"    # Sugestões revisadas pelo clínico
    ADJUSTMENTS_CONFIRMED = "adjustments_confirmed"  # Ajustes confirmados
    GEOMETRY_GENERATED = "geometry_generated"    # Geometria 3D gerada
    READY_FOR_EXPORT = "ready_for_export"        # Pronto para exportar STL
    EXPORTED = "exported"                        # STL exportado
    PRINTED = "printed"                          # Palmilha impressa
    DELIVERED = "delivered"                      # Entregue ao paciente
    FEEDBACK_COLLECTED = "feedback_collected"    # Feedback clínico coletado
    ARCHIVED = "archived"                        # Caso arquivado


class PatientInfo(BaseModel):
    """Informações básicas do paciente."""

    patient_id: str = Field(..., description="ID único do paciente")
    name: str = Field(..., description="Nome do paciente")
    age: int = Field(..., ge=0, le=150, description="Idade em anos")
    gender: str = Field(..., description="Gênero (M/F/Outro)")

    # Dados clínicos
    main_complaint: str = Field(..., description="Queixa principal")
    medical_history: Optional[str] = Field(default=None, description="Histórico médico relevante")
    current_medications: Optional[str] = Field(default=None, description="Medicações em uso")

    # Contato
    phone: Optional[str] = Field(default=None, description="Telefone de contato")
    email: Optional[str] = Field(default=None, description="Email")


class ClinicalCase(BaseModel):
    """
    Caso clínico completo: paciente, análise, sugestões, ajustes e resultado.
    Representa todo o ciclo de vida de um caso desde início até feedback.
    """

    case_id: str = Field(..., description="ID único do caso (UUID)")

    # ========== PACIENTE ==========
    patient: PatientInfo = Field(..., description="Informações do paciente")

    # ========== WORKFLOW ==========
    status: CaseStatus = Field(default=CaseStatus.CREATED, description="Estado atual do caso")

    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criação")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Última atualização")

    # ========== ENTRADA (IMAGENS) ==========
    scan_image_path: Optional[str] = Field(
        default=None,
        description="Caminho da imagem original do pé"
    )

    scan_metadata: Optional[dict] = Field(
        default=None,
        description="Metadados da imagem (resolução, data, etc)"
    )

    # ========== ANÁLISE BIOMECÂNICA ==========
    biomechanical_profile: Optional[dict] = Field(
        default=None,
        description="Perfil biomecânico extraído (serializado BiomechanicalFootProfile)"
    )

    analysis_confidence: Optional[float] = Field(
        default=None,
        ge=0, le=1,
        description="Confiança da análise (0-1)"
    )

    analysis_notes: Optional[str] = Field(
        default=None,
        description="Notas do analista sobre qualidade/observações"
    )

    # ========== SUGESTÕES CLÍNICAS ==========
    suggestions: List[dict] = Field(
        default_factory=list,
        description="Sugestões clínicas geradas (serializadas ClinicalSuggestion)"
    )

    primary_condition: Optional[str] = Field(
        default=None,
        description="Condição principal detectada"
    )

    secondary_conditions: List[str] = Field(
        default_factory=list,
        description="Condições secundárias detectadas"
    )

    # ========== AJUSTES APLICADOS ==========
    insole_parameters: Optional[dict] = Field(
        default=None,
        description="Parâmetros da palmilha finais (serializado InsoleParameterSet)"
    )

    clinician_id: Optional[str] = Field(
        default=None,
        description="ID do clínico que revisou/confirmou"
    )

    clinician_notes: Optional[str] = Field(
        default=None,
        description="Notas do clínico durante revisão"
    )

    parameters_modified_by_clinician: bool = Field(
        default=False,
        description="Se o clínico modificou os parâmetros sugeridos"
    )

    # ========== GEOMETRIA 3D E EXPORTAÇÃO ==========
    stl_file_path: Optional[str] = Field(
        default=None,
        description="Caminho do arquivo STL gerado"
    )

    stl_generated_at: Optional[datetime] = Field(
        default=None,
        description="Data/hora de geração do STL"
    )

    geometry_notes: Optional[str] = Field(
        default=None,
        description="Notas sobre a geometria gerada"
    )

    # ========== FEEDBACK E APRENDIZADO ==========
    clinical_feedback: Optional[str] = Field(
        default=None,
        description="Feedback do clínico após uso (ex: efetividade, ajustes necessários)"
    )

    patient_feedback: Optional[str] = Field(
        default=None,
        description="Feedback do paciente (conforto, funcionalidade, etc)"
    )

    feedback_collected_at: Optional[datetime] = Field(
        default=None,
        description="Data de coleta do feedback"
    )

    # ========== CONTROLE DE QUALIDADE ==========
    quality_score: Optional[float] = Field(
        default=None,
        ge=0, le=1,
        description="Pontuação de qualidade geral do caso"
    )

    issues_encountered: List[str] = Field(
        default_factory=list,
        description="Problemas encontrados durante o processo"
    )

    # ========== TAGS E CLASSIFICAÇÃO ==========
    tags: List[str] = Field(
        default_factory=list,
        description="Tags para classificação (ex: 'complex', 'high-confidence', 'learning')"
    )

    learning_case: bool = Field(
        default=False,
        description="Se este caso foi marcado como caso de aprendizado"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "case-abc123",
                "patient": {
                    "patient_id": "pat-001",
                    "name": "João Silva",
                    "age": 45,
                    "gender": "M",
                    "main_complaint": "Dor no arco medial ao caminhar",
                    "medical_history": "Histórico de pé plano desde infância"
                },
                "status": "analyzed",
                "created_at": "2026-09-23T10:30:00Z",
                "updated_at": "2026-09-23T11:00:00Z",
                "scan_image_path": "/cases/case-abc123/scan.jpg",
                "biomechanical_profile": {
                    "foot_length": 250.0,
                    "arch_index": 0.18,
                    "foot_type": "flat"
                },
                "analysis_confidence": 0.88,
                "primary_condition": "flatfoot",
                "secondary_conditions": [],
                "tags": ["high-confidence"]
            }
        }

    def is_ready_for_geometry_generation(self) -> bool:
        """Verifica se o caso está pronto para gerar geometria 3D."""
        return (
            self.status in [CaseStatus.ADJUSTMENTS_CONFIRMED, CaseStatus.GEOMETRY_GENERATED]
            and self.insole_parameters is not None
        )

    def is_ready_for_export(self) -> bool:
        """Verifica se o caso está pronto para exportar STL."""
        return (
            self.status >= CaseStatus.GEOMETRY_GENERATED
            and self.stl_file_path is not None
        )

    def has_complete_feedback(self) -> bool:
        """Verifica se o caso tem feedback completo."""
        return (
            self.status == CaseStatus.FEEDBACK_COLLECTED
            and self.clinical_feedback is not None
            and self.patient_feedback is not None
        )


class CaseAnalysisResult(BaseModel):
    """Resultado de uma análise de caso (para resposta de API)."""

    case_id: str = Field(..., description="ID do caso analisado")
    status: CaseStatus = Field(..., description="Status após análise")

    biomechanical_profile: Optional[dict] = Field(
        default=None,
        description="Perfil biomecânico extraído"
    )

    conditions_detected: List[str] = Field(
        ...,
        description="Condições detectadas"
    )

    suggestions: List[dict] = Field(
        ...,
        description="Sugestões clínicas"
    )

    analysis_confidence: float = Field(
        ..., ge=0, le=1,
        description="Confiança geral da análise"
    )

    next_steps: List[str] = Field(
        ...,
        description="Próximos passos recomendados"
    )


class CaseExportRequest(BaseModel):
    """Requisição para exportar caso como STL."""

    case_id: str = Field(..., description="ID do caso")
    export_format: str = Field(
        default="stl",
        description="Formato de exportação (stl, step, iges, etc)"
    )
    export_quality: str = Field(
        default="medium",
        description="Qualidade da malha (low, medium, high, ultra)"
    )

    include_metadata: bool = Field(
        default=True,
        description="Incluir metadados no arquivo"
    )


class CaseFeedbackRequest(BaseModel):
    """Requisição para registrar feedback de um caso."""

    case_id: str = Field(..., description="ID do caso")

    clinical_feedback: Optional[str] = Field(
        default=None,
        description="Feedback do clínico"
    )

    patient_feedback: Optional[str] = Field(
        default=None,
        description="Feedback do paciente"
    )

    effectiveness_score: Optional[float] = Field(
        default=None, ge=0, le=10,
        description="Pontuação de efetividade (0-10)"
    )

    comfort_score: Optional[float] = Field(
        default=None, ge=0, le=10,
        description="Pontuação de conforto (0-10)"
    )

    issues: Optional[List[str]] = Field(
        default=None,
        description="Problemas identificados"
    )

    should_be_learning_case: bool = Field(
        default=False,
        description="Marcar como caso de aprendizado"
    )
