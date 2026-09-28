"""
Modelos clínicos para regras de sugestão e ajustes paramétricos.
Estrutura que captura conhecimento biomecânico em regras com confiança.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum


class ConditionType(str, Enum):
    """Tipos de condições patológicas detectadas."""
    FLATFOOT = "flatfoot"
    CAVUSFOOT = "cavusfoot"
    HALLUX_VALGUS = "hallux_valgus"
    EXCESSIVE_PRONATION = "excessive_pronation"
    METATARSALGIA = "metatarsalgia"
    PLANTAR_FASCIITIS = "plantar_fasciitis"
    NORMAL = "normal"


class ParameterAdjustment(BaseModel):
    """
    Um ajuste recomendado para um parâmetro da palmilha.
    Inclui o valor sugerido e a razão clínica.
    """

    parameter_name: str = Field(..., description="Nome do parâmetro (ex: arch_height_medial)")
    suggested_value: float = Field(..., description="Valor sugerido")
    min_safe_value: float = Field(..., description="Mínimo seguro")
    max_safe_value: float = Field(..., description="Máximo seguro")
    reason: str = Field(..., description="Explicação clínica para este ajuste")
    priority: int = Field(default=1, ge=1, le=5, description="Prioridade (1=alta, 5=baixa)")


class ClinicalRule(BaseModel):
    """
    Uma regra clínica que mapeia biomecânica → sugestões de parâmetros.
    Detecta condições e propõe ajustes com confiança.
    """

    rule_id: str = Field(..., description="ID único da regra (ex: FLATFOOT_001)")
    condition_type: ConditionType = Field(..., description="Tipo de condição detectada")
    condition_name: str = Field(..., description="Nome legível da condição")

    # Critérios de detecção
    detection_criteria: str = Field(
        ...,
        description="Descrição dos critérios de detecção (ex: arch_index < 0.21)"
    )

    # Ajustes paramétricos
    parameter_adjustments: List[ParameterAdjustment] = Field(
        ...,
        description="Lista de ajustes sugeridos (ordenado por prioridade)"
    )

    # Confiança e validação
    confidence_threshold: float = Field(
        default=0.7,
        ge=0, le=1,
        description="Limite de confiança para aplicar a regra (0-1)"
    )

    clinical_evidence: str = Field(
        ...,
        description="Evidência clínica que suporta esta regra"
    )

    contraindications: List[str] = Field(
        default_factory=list,
        description="Condições onde esta regra NÃO deve ser aplicada"
    )

    references: List[str] = Field(
        default_factory=list,
        description="Referências bibliográficas (opcional)"
    )

    # Metadados
    version: str = Field(default="1.0", description="Versão da regra")
    created_date: str = Field(default="2026-09-23", description="Data de criação")
    last_modified: str = Field(default="2026-09-23", description="Última modificação")

    def calculate_confidence(self, biomechanical_profile) -> float:
        """
        Calcula confiança desta regra para um perfil biomecânico específico.
        Returns: float entre 0 e 1
        """
        # Implementação básica - pode ser refinada com ML
        # Para agora: se detecta a condição, retorna confidence_threshold
        if self._detects_condition(biomechanical_profile):
            return self.confidence_threshold
        return 0.0

    def _detects_condition(self, biomechanical_profile) -> bool:
        """
        Verifica se o perfil biomecânico satisfaz os critérios de detecção.
        """
        # Implementação simplificada - será expandida com lógica específica
        if self.condition_type == ConditionType.FLATFOOT:
            return biomechanical_profile.is_flatfoot
        elif self.condition_type == ConditionType.CAVUSFOOT:
            return biomechanical_profile.is_cavusfoot
        elif self.condition_type == ConditionType.HALLUX_VALGUS:
            return biomechanical_profile.has_hallux_valgus
        elif self.condition_type == ConditionType.EXCESSIVE_PRONATION:
            return biomechanical_profile.is_pronated
        return False

    def get_ordered_adjustments(self) -> List[ParameterAdjustment]:
        """Retorna ajustes ordenados por prioridade."""
        return sorted(self.parameter_adjustments, key=lambda x: x.priority)


class ClinicalSuggestion(BaseModel):
    """
    Uma sugestão clínica gerada pela aplicação de uma ou mais regras.
    Agrupa ajustes relacionados com razão unificada.
    """

    suggestion_id: str = Field(..., description="ID único (UUID)")

    # Condição detectada
    condition_type: ConditionType = Field(..., description="Tipo de condição principal")
    condition_name: str = Field(..., description="Nome da condição detectada")

    # Confiança e evidência
    confidence: float = Field(
        ..., ge=0, le=1,
        description="Confiança geral da sugestão (média ponderada)"
    )

    clinical_rationale: str = Field(
        ...,
        description="Explicação clínica consolidada"
    )

    # Ajustes
    parameter_adjustments: List[ParameterAdjustment] = Field(
        ...,
        description="Ajustes recomendados"
    )

    # Origem
    applied_rules: List[str] = Field(
        ...,
        description="IDs das regras que geraram esta sugestão"
    )

    # Status
    is_confirmed: bool = Field(
        default=False,
        description="Se foi confirmada pelo clínico"
    )

    requires_confirmation: bool = Field(
        default=False,
        description="Se requer confirmação manual (parâmetros incomuns)"
    )

    confirmation_notes: Optional[str] = Field(
        default=None,
        description="Notas do clínico após revisão"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "suggestion_id": "sug-abc123",
                "condition_type": "flatfoot",
                "condition_name": "Pé Plano",
                "confidence": 0.85,
                "clinical_rationale": "Índice do arco baixo detectado; elevação medial recomendada para melhorar suporte lateral e reduzir pronação excessiva.",
                "parameter_adjustments": [
                    {
                        "parameter_name": "arch_height_medial",
                        "suggested_value": 6.0,
                        "min_safe_value": 0.0,
                        "max_safe_value": 12.0,
                        "reason": "Elevação do arco para suportar medial longitudinal",
                        "priority": 1
                    }
                ],
                "applied_rules": ["FLATFOOT_001", "PRONATION_002"],
                "is_confirmed": False,
                "requires_confirmation": False
            }
        }
