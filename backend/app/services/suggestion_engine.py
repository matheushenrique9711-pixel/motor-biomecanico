"""
Motor de sugestões clínicas.
Aplica regras clínicas ao perfil biomecânico e gera sugestões parametrizadas.
"""

from typing import List, Dict, Optional
import uuid
from datetime import datetime

from app.models import (
    BiomechanicalFootProfile,
    ClinicalRule,
    ClinicalSuggestion,
    ParameterAdjustment,
    ConditionType,
)


class SuggestionEngine:
    """
    Motor de sugestões que:
    1. Recebe um perfil biomecânico
    2. Aplica regras clínicas com cálculo de confiança
    3. Gera sugestões consolidadas de parâmetros
    4. Prioriza ajustes por importância clínica
    """

    def __init__(self):
        """Inicializa o motor com regras clínicas padrão."""
        self.clinical_rules = self._load_default_rules()

    def _load_default_rules(self) -> List[ClinicalRule]:
        """
        Carrega as regras clínicas padrão do sistema.
        Em produção, estas viriam de um banco de dados.
        """
        rules = [
            self._create_flatfoot_rule(),
            self._create_cavusfoot_rule(),
            self._create_hallux_valgus_rule(),
            self._create_excessive_pronation_rule(),
            self._create_metatarsalgia_rule(),
        ]
        return rules

    def _create_flatfoot_rule(self) -> ClinicalRule:
        """Regra para pé plano (arch_index < 0.21)."""
        return ClinicalRule(
            rule_id="FLATFOOT_001",
            condition_type=ConditionType.FLATFOOT,
            condition_name="Pé Plano",
            detection_criteria="arch_index < 0.21",
            parameter_adjustments=[
                ParameterAdjustment(
                    parameter_name="arch_height_medial",
                    suggested_value=6.0,
                    min_safe_value=0.0,
                    max_safe_value=12.0,
                    reason="Elevação do arco medial para restaurar suporte lateral e reduzir pronação",
                    priority=1,
                ),
                ParameterAdjustment(
                    parameter_name="medial_arch_stiffness",
                    suggested_value=1.3,
                    min_safe_value=0.8,
                    max_safe_value=1.6,
                    reason="Aumentar rigidez medial para suportar arco baixo",
                    priority=2,
                ),
                ParameterAdjustment(
                    parameter_name="heel_cup_depth_mm",
                    suggested_value=3.0,
                    min_safe_value=0.0,
                    max_safe_value=6.0,
                    reason="Cúpula calcanear para melhorar estabilidade posterior",
                    priority=3,
                ),
            ],
            confidence_threshold=0.85,
            clinical_evidence=(
                "Pés planos apresentam perda da curva do arco longitudinal medial. "
                "Palmilhas com elevação do arco reduzem pronação excessiva e carga em estruturas mediais (ligamentos, fáscia plantar). "
                "Estudos biomecânicos mostram redução de 15-25% na pressão plantar com arch support adequado."
            ),
            contraindications=[
                "Cavus foot (não elevar mais se já muito elevado)",
                "Rigidez muito severa (pode causar desconforto)",
            ],
            version="1.0",
            created_date="2026-09-23",
        )

    def _create_cavusfoot_rule(self) -> ClinicalRule:
        """Regra para pé cavo (arch_index > 0.26)."""
        return ClinicalRule(
            rule_id="CAVUSFOOT_001",
            condition_type=ConditionType.CAVUSFOOT,
            condition_name="Pé Cavo",
            detection_criteria="arch_index > 0.26 AND medial_incline_angle > 5",
            parameter_adjustments=[
                ParameterAdjustment(
                    parameter_name="arch_height_medial",
                    suggested_value=2.0,
                    min_safe_value=0.0,
                    max_safe_value=6.0,
                    reason="Manter arco moderado; evitar elevação que piore o cavus",
                    priority=1,
                ),
                ParameterAdjustment(
                    parameter_name="metatarsal_dome_height",
                    suggested_value=4.0,
                    min_safe_value=0.0,
                    max_safe_value=8.0,
                    reason="Cúpula metatarsal para distribuir pressão no antepé",
                    priority=2,
                ),
                ParameterAdjustment(
                    parameter_name="medial_arch_stiffness",
                    suggested_value=0.9,
                    min_safe_value=0.8,
                    max_safe_value=1.6,
                    reason="Reduzir rigidez para permitir adaptação (arco já rígido)",
                    priority=3,
                ),
            ],
            confidence_threshold=0.80,
            clinical_evidence=(
                "Pés cavos apresentam arco excessivamente elevado com pronação supinada. "
                "O suporte deve focar em distribuição de carga e alivio de pontos de alta pressão (calcâneo, metatarsos). "
                "Aumentar cúpula metatarsal reduz carga concentrada no antepé."
            ),
            contraindications=[
                "Não usar elevação de arco agressiva",
            ],
            version="1.0",
            created_date="2026-09-23",
        )

    def _create_hallux_valgus_rule(self) -> ClinicalRule:
        """Regra para hálux valgo (bunion/joanete)."""
        return ClinicalRule(
            rule_id="HALLUX_VALGUS_001",
            condition_type=ConditionType.HALLUX_VALGUS,
            condition_name="Hálux Valgo (Joanete)",
            detection_criteria="hallux_valgus_angle > 15 OR bunion_relief_depth present",
            parameter_adjustments=[
                ParameterAdjustment(
                    parameter_name="mt1_dome_height",
                    suggested_value=3.5,
                    min_safe_value=0.0,
                    max_safe_value=6.0,
                    reason="Cúpula MT1 para suportar o hálux e reduzir pronação",
                    priority=1,
                ),
                ParameterAdjustment(
                    parameter_name="bunion_relief_depth",
                    suggested_value=-2.5,
                    min_safe_value=-4.0,
                    max_safe_value=0.0,
                    reason="Recesso lateral MT1 para aliviar pressão na proeminência óssea",
                    priority=2,
                ),
                ParameterAdjustment(
                    parameter_name="mt1_medial_extension",
                    suggested_value=5.0,
                    min_safe_value=0.0,
                    max_safe_value=10.0,
                    reason="Extensão medial do MT1 para suporte longitudinal",
                    priority=3,
                ),
            ],
            confidence_threshold=0.82,
            clinical_evidence=(
                "Hálux valgo resulta em desalinhamento do primeiro metatarso. "
                "Palmilhas com suporte MT1 e recesso para joanete reduzem dor e pressão local. "
                "Estudos mostram melhora de 20-30% em conforto com suporte adequado."
            ),
            contraindications=[],
            version="1.0",
            created_date="2026-09-23",
        )

    def _create_excessive_pronation_rule(self) -> ClinicalRule:
        """Regra para pronação excessiva (subtalar_inversion_angle < -8°)."""
        return ClinicalRule(
            rule_id="PRONATION_001",
            condition_type=ConditionType.EXCESSIVE_PRONATION,
            condition_name="Pronação Excessiva",
            detection_criteria="subtalar_inversion_angle < -8 OR is_pronated property true",
            parameter_adjustments=[
                ParameterAdjustment(
                    parameter_name="lateral_wedge_angle",
                    suggested_value=5.0,
                    min_safe_value=0.0,
                    max_safe_value=10.0,
                    reason="Cunha lateral para controlar supinação e reduzir pronação dinâmica",
                    priority=1,
                ),
                ParameterAdjustment(
                    parameter_name="arch_height_medial",
                    suggested_value=4.0,
                    min_safe_value=0.0,
                    max_safe_value=12.0,
                    reason="Elevação medial para suportar arco durante locomoção",
                    priority=2,
                ),
                ParameterAdjustment(
                    parameter_name="heel_cup_depth_mm",
                    suggested_value=4.0,
                    min_safe_value=0.0,
                    max_safe_value=6.0,
                    reason="Cúpula calcanear profunda para controle pós-talâmico",
                    priority=3,
                ),
            ],
            confidence_threshold=0.83,
            clinical_evidence=(
                "Pronação excessiva aumenta carga em estruturas mediais e causa dor plantar. "
                "Combinação de cunha lateral + elevação do arco reduz ângulo de subtalar. "
                "Melhora documentada em marcha e redução de dor."
            ),
            contraindications=[
                "Cavus foot supinado (evitar cunha que aumente supinação)",
            ],
            version="1.0",
            created_date="2026-09-23",
        )

    def _create_metatarsalgia_rule(self) -> ClinicalRule:
        """Regra para metatarsalgia (dor antepé)."""
        return ClinicalRule(
            rule_id="METATARSALGIA_001",
            condition_type=ConditionType.METATARSALGIA,
            condition_name="Metatarsalgia",
            detection_criteria=(
                "load_distribution.central_metatarsal > 0.30 OR "
                "high_forefoot_pressure_regions detected"
            ),
            parameter_adjustments=[
                ParameterAdjustment(
                    parameter_name="metatarsal_dome_height",
                    suggested_value=5.0,
                    min_safe_value=0.0,
                    max_safe_value=8.0,
                    reason="Cúpula metatarsal para distribuir pressão no antepé",
                    priority=1,
                ),
                ParameterAdjustment(
                    parameter_name="forefoot_rocker_radius",
                    suggested_value=30.0,
                    min_safe_value=15.0,
                    max_safe_value=40.0,
                    reason="Rocker antepé para facilitar rol e reduzir pressão máxima",
                    priority=2,
                ),
                ParameterAdjustment(
                    parameter_name="morton_neuroma_relief_mm",
                    suggested_value=2.0,
                    min_safe_value=0.0,
                    max_safe_value=4.0,
                    reason="Recesso intermetatarsal para aliviar neuroma se presente",
                    priority=3,
                ),
            ],
            confidence_threshold=0.78,
            clinical_evidence=(
                "Metatarsalgia resulta de sobrecarga no antepé. "
                "Cúpulas metatarsais e rocker reduzem pico de pressão em 15-40%. "
                "Melhora significativa em conforto dinâmico."
            ),
            contraindications=[],
            version="1.0",
            created_date="2026-09-23",
        )

    def generate_suggestions(
        self,
        biomechanical_profile: BiomechanicalFootProfile,
        override_rules: Optional[List[ClinicalRule]] = None,
    ) -> List[ClinicalSuggestion]:
        """
        Analisa um perfil biomecânico e gera sugestões clínicas.

        Args:
            biomechanical_profile: Perfil extraído do escaneamento
            override_rules: Regras customizadas (opcional)

        Returns:
            Lista de sugestões clínicas ordenadas por confiança
        """
        rules = override_rules or self.clinical_rules
        suggestions = []

        for rule in rules:
            confidence = rule.calculate_confidence(biomechanical_profile)

            if confidence >= rule.confidence_threshold:
                suggestion = self._create_suggestion_from_rule(
                    rule=rule,
                    biomechanical_profile=biomechanical_profile,
                    confidence=confidence,
                )
                suggestions.append(suggestion)

        # Ordena por confiança (descrescente)
        suggestions.sort(key=lambda s: s.confidence, reverse=True)

        return suggestions

    def _create_suggestion_from_rule(
        self,
        rule: ClinicalRule,
        biomechanical_profile: BiomechanicalFootProfile,
        confidence: float,
    ) -> ClinicalSuggestion:
        """Cria uma ClinicalSuggestion a partir de uma regra aplicada."""

        # Ajusta valores sugeridos com base no perfil específico
        adjusted_adjustments = self._adjust_parameters_for_profile(
            rule.parameter_adjustments,
            biomechanical_profile,
        )

        return ClinicalSuggestion(
            suggestion_id=f"sug-{uuid.uuid4().hex[:8]}",
            condition_type=rule.condition_type,
            condition_name=rule.condition_name,
            confidence=confidence,
            clinical_rationale=rule.clinical_evidence,
            parameter_adjustments=adjusted_adjustments,
            applied_rules=[rule.rule_id],
            is_confirmed=False,
            requires_confirmation=self._check_requires_confirmation(adjusted_adjustments),
        )

    def _adjust_parameters_for_profile(
        self,
        adjustments: List[ParameterAdjustment],
        profile: BiomechanicalFootProfile,
    ) -> List[ParameterAdjustment]:
        """
        Ajusta valores sugeridos com base no perfil específico.
        Pode aplicar modulação suave dos parâmetros.
        """
        # Implementação básica: retorna os ajustes sem modificação
        # Em versão refinada, poderia fazer interpolação baseada em severidade
        return adjustments

    def _check_requires_confirmation(self, adjustments: List[ParameterAdjustment]) -> bool:
        """
        Verifica se algum ajuste é "incomum" e requer confirmação manual.
        Ex: valores muito altos ou muito baixos.
        """
        for adj in adjustments:
            # Se o valor sugerido está próximo dos extremos, requer confirmação
            range_size = adj.max_safe_value - adj.min_safe_value
            margin_from_min = adj.suggested_value - adj.min_safe_value
            margin_from_max = adj.max_safe_value - adj.suggested_value

            # Se está nos 20% extremos, marcar como incomum
            if margin_from_min < 0.2 * range_size or margin_from_max < 0.2 * range_size:
                return True

        return False

    def merge_suggestions(self, suggestions: List[ClinicalSuggestion]) -> ClinicalSuggestion:
        """
        Consolida múltiplas sugestões em uma única sugestão composta.
        Usa a primeira (maior confiança) como base e agrega ajustes.
        """
        if not suggestions:
            raise ValueError("Nenhuma sugestão para consolidar")

        primary = suggestions[0]  # Maior confiança

        # Consolida todos os ajustes, removendo duplicatas
        all_adjustments = {}
        for suggestion in suggestions:
            for adj in suggestion.parameter_adjustments:
                if adj.parameter_name not in all_adjustments:
                    all_adjustments[adj.parameter_name] = adj
                else:
                    # Se já existe, usa o de maior prioridade (menor número)
                    existing = all_adjustments[adj.parameter_name]
                    if adj.priority < existing.priority:
                        all_adjustments[adj.parameter_name] = adj

        # Calcula confiança média
        avg_confidence = sum(s.confidence for s in suggestions) / len(suggestions)

        return ClinicalSuggestion(
            suggestion_id=f"sug-{uuid.uuid4().hex[:8]}",
            condition_type=primary.condition_type,
            condition_name=primary.condition_name,
            confidence=avg_confidence,
            clinical_rationale=(
                f"Consolidação de {len(suggestions)} sugestões. "
                f"Primária: {primary.condition_name}"
            ),
            parameter_adjustments=sorted(
                all_adjustments.values(),
                key=lambda x: x.priority,
            ),
            applied_rules=[
                rule_id
                for suggestion in suggestions
                for rule_id in suggestion.applied_rules
            ],
            requires_confirmation=any(s.requires_confirmation for s in suggestions),
        )
