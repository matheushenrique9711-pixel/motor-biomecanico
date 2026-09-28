"""
Gerenciador de casos clínicos.
Responsável por persistência, atualização de status e consultas de casos.
"""

from typing import List, Optional
import uuid
from datetime import datetime

from app.models import (
    ClinicalCase,
    CaseStatus,
    PatientInfo,
    BiomechanicalFootProfile,
    ClinicalSuggestion,
    InsoleParameterSet,
)


class CaseManager:
    """
    Gerencia todo o ciclo de vida de um caso clínico.
    Em desenvolvimento: usa armazenamento em memória.
    Em produção: será integrado com SQLAlchemy + PostgreSQL.
    """

    def __init__(self):
        """Inicializa o gerenciador com armazenamento em memória."""
        # Em produção, seria uma conexão com banco de dados
        self._cases_store: dict[str, ClinicalCase] = {}
        self._patients_store: dict[str, PatientInfo] = {}

    # ========== CRIAÇÃO DE CASOS ==========

    def create_case(
        self,
        patient_info: PatientInfo,
        scan_image_path: Optional[str] = None,
        scan_metadata: Optional[dict] = None,
    ) -> ClinicalCase:
        """
        Cria um novo caso clínico para um paciente.

        Args:
            patient_info: Informações básicas do paciente
            scan_image_path: Caminho da imagem do escaneamento
            scan_metadata: Metadados da imagem

        Returns:
            ClinicalCase criado
        """
        case_id = f"case-{uuid.uuid4().hex[:8]}"

        case = ClinicalCase(
            case_id=case_id,
            patient=patient_info,
            status=CaseStatus.CREATED,
            scan_image_path=scan_image_path,
            scan_metadata=scan_metadata,
        )

        self._cases_store[case_id] = case
        return case

    # ========== LEITURA DE CASOS ==========

    def get_case(self, case_id: str) -> Optional[ClinicalCase]:
        """Recupera um caso pelo ID."""
        return self._cases_store.get(case_id)

    def get_patient_cases(self, patient_id: str) -> List[ClinicalCase]:
        """Retorna todos os casos de um paciente."""
        return [
            case for case in self._cases_store.values()
            if case.patient.patient_id == patient_id
        ]

    def list_cases(
        self,
        status: Optional[CaseStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[ClinicalCase]:
        """
        Lista casos com filtros opcionais.

        Args:
            status: Filtrar por status (opcional)
            limit: Número máximo de casos
            offset: Deslocamento para paginação

        Returns:
            Lista de casos
        """
        cases = list(self._cases_store.values())

        if status:
            cases = [c for c in cases if c.status == status]

        # Ordena por data de criação decrescente
        cases.sort(key=lambda c: c.created_at, reverse=True)

        return cases[offset : offset + limit]

    def get_cases_by_condition(
        self,
        condition: str,
        limit: int = 50,
    ) -> List[ClinicalCase]:
        """Retorna casos com uma condição específica."""
        return [
            case for case in self._cases_store.values()
            if case.primary_condition == condition
            and case.status in [
                CaseStatus.ANALYZED,
                CaseStatus.SUGGESTIONS_REVIEWED,
                CaseStatus.DELIVERED,
                CaseStatus.FEEDBACK_COLLECTED,
            ]
        ][:limit]

    # ========== ATUALIZAÇÃO DE STATUS ==========

    def update_case_status(
        self,
        case_id: str,
        new_status: CaseStatus,
        notes: Optional[str] = None,
    ) -> ClinicalCase:
        """
        Atualiza o status de um caso.

        Args:
            case_id: ID do caso
            new_status: Novo status
            notes: Notas opcionais

        Returns:
            Caso atualizado
        """
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")

        case.status = new_status
        case.updated_at = datetime.utcnow()

        return case

    # ========== ANÁLISE BIOMECÂNICA ==========

    def update_biomechanical_analysis(
        self,
        case_id: str,
        biomechanical_profile: BiomechanicalFootProfile,
        analysis_confidence: float,
        notes: Optional[str] = None,
    ) -> ClinicalCase:
        """
        Registra análise biomecânica no caso.

        Args:
            case_id: ID do caso
            biomechanical_profile: Perfil extraído
            analysis_confidence: Confiança da análise (0-1)
            notes: Notas do analista

        Returns:
            Caso atualizado
        """
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")

        case.biomechanical_profile = biomechanical_profile.dict()
        case.analysis_confidence = analysis_confidence
        case.analysis_notes = notes
        case.status = CaseStatus.ANALYZED
        case.updated_at = datetime.utcnow()

        # Detecta condições primárias
        if biomechanical_profile.is_flatfoot:
            case.primary_condition = "flatfoot"
        elif biomechanical_profile.is_cavusfoot:
            case.primary_condition = "cavusfoot"
        elif biomechanical_profile.has_hallux_valgus:
            case.primary_condition = "hallux_valgus"
        elif biomechanical_profile.is_pronated:
            case.primary_condition = "excessive_pronation"
        else:
            case.primary_condition = "normal"

        return case

    # ========== SUGESTÕES CLÍNICAS ==========

    def add_suggestions(
        self,
        case_id: str,
        suggestions: List[ClinicalSuggestion],
    ) -> ClinicalCase:
        """
        Adiciona sugestões clínicas geradas ao caso.

        Args:
            case_id: ID do caso
            suggestions: Lista de sugestões

        Returns:
            Caso atualizado
        """
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")

        case.suggestions = [s.dict() for s in suggestions]
        case.status = CaseStatus.SUGGESTIONS_GENERATED
        case.updated_at = datetime.utcnow()

        # Detecta se alguma sugestão requer confirmação
        if any(s.requires_confirmation for s in suggestions):
            case.tags.append("requires-confirmation")

        return case

    def confirm_suggestions(
        self,
        case_id: str,
        clinician_id: str,
        clinician_notes: Optional[str] = None,
    ) -> ClinicalCase:
        """
        Marca sugestões como revisadas/confirmadas pelo clínico.

        Args:
            case_id: ID do caso
            clinician_id: ID do clínico
            clinician_notes: Notas do clínico

        Returns:
            Caso atualizado
        """
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")

        case.status = CaseStatus.SUGGESTIONS_REVIEWED
        case.clinician_id = clinician_id
        case.clinician_notes = clinician_notes
        case.updated_at = datetime.utcnow()

        return case

    # ========== PARÂMETROS DA PALMILHA ==========

    def update_insole_parameters(
        self,
        case_id: str,
        parameters: InsoleParameterSet,
        modified_by_clinician: bool = False,
    ) -> ClinicalCase:
        """
        Registra os parâmetros finais da palmilha no caso.

        Args:
            case_id: ID do caso
            parameters: InsoleParameterSet final
            modified_by_clinician: Se foi modificado pelo clínico

        Returns:
            Caso atualizado
        """
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")

        case.insole_parameters = parameters.dict()
        case.parameters_modified_by_clinician = modified_by_clinician
        case.status = CaseStatus.ADJUSTMENTS_CONFIRMED
        case.updated_at = datetime.utcnow()

        return case

    # ========== GEOMETRIA E EXPORTAÇÃO ==========

    def register_stl_export(
        self,
        case_id: str,
        stl_file_path: str,
        geometry_notes: Optional[str] = None,
    ) -> ClinicalCase:
        """
        Registra a geração e exportação de geometria STL.

        Args:
            case_id: ID do caso
            stl_file_path: Caminho do arquivo STL
            geometry_notes: Notas sobre a geometria

        Returns:
            Caso atualizado
        """
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")

        case.stl_file_path = stl_file_path
        case.stl_generated_at = datetime.utcnow()
        case.geometry_notes = geometry_notes
        case.status = CaseStatus.GEOMETRY_GENERATED
        case.updated_at = datetime.utcnow()

        return case

    def mark_as_exported(self, case_id: str) -> ClinicalCase:
        """Marca caso como STL exportado."""
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")

        case.status = CaseStatus.EXPORTED
        case.updated_at = datetime.utcnow()

        return case

    # ========== FEEDBACK E APRENDIZADO ==========

    def add_clinical_feedback(
        self,
        case_id: str,
        clinical_feedback: str,
        issues: Optional[List[str]] = None,
    ) -> ClinicalCase:
        """
        Registra feedback do clínico após uso da palmilha.

        Args:
            case_id: ID do caso
            clinical_feedback: Comentários clínicos
            issues: Problemas identificados

        Returns:
            Caso atualizado
        """
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")

        case.clinical_feedback = clinical_feedback
        if issues:
            case.issues_encountered = issues
        case.updated_at = datetime.utcnow()

        return case

    def add_patient_feedback(
        self,
        case_id: str,
        patient_feedback: str,
        effectiveness_score: Optional[float] = None,
        comfort_score: Optional[float] = None,
    ) -> ClinicalCase:
        """
        Registra feedback do paciente.

        Args:
            case_id: ID do caso
            patient_feedback: Comentários do paciente
            effectiveness_score: Pontuação de efetividade (0-10)
            comfort_score: Pontuação de conforto (0-10)

        Returns:
            Caso atualizado
        """
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")

        case.patient_feedback = patient_feedback
        case.feedback_collected_at = datetime.utcnow()
        case.status = CaseStatus.FEEDBACK_COLLECTED
        case.updated_at = datetime.utcnow()

        # Calcula quality score baseado em feedbacks
        if effectiveness_score is not None and comfort_score is not None:
            case.quality_score = (effectiveness_score + comfort_score) / 20.0  # Normaliza a 0-1

        return case

    def mark_as_learning_case(self, case_id: str) -> ClinicalCase:
        """Marca caso como importante para aprendizado contínuo."""
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Caso {case_id} não encontrado")

        case.learning_case = True
        case.tags.append("learning")
        case.updated_at = datetime.utcnow()

        return case

    # ========== ESTATÍSTICAS ==========

    def get_statistics(self) -> dict:
        """Retorna estatísticas gerais dos casos."""
        cases = list(self._cases_store.values())

        if not cases:
            return {
                "total_cases": 0,
                "by_status": {},
                "by_condition": {},
                "average_confidence": 0.0,
                "learning_cases": 0,
            }

        # Por status
        by_status = {}
        for case in cases:
            status = case.status.value
            by_status[status] = by_status.get(status, 0) + 1

        # Por condição
        by_condition = {}
        for case in cases:
            if case.primary_condition:
                cond = case.primary_condition
                by_condition[cond] = by_condition.get(cond, 0) + 1

        # Confiança média
        analyzed_cases = [c for c in cases if c.analysis_confidence is not None]
        avg_confidence = (
            sum(c.analysis_confidence for c in analyzed_cases) / len(analyzed_cases)
            if analyzed_cases
            else 0.0
        )

        # Casos de aprendizado
        learning_cases = len([c for c in cases if c.learning_case])

        return {
            "total_cases": len(cases),
            "by_status": by_status,
            "by_condition": by_condition,
            "average_confidence": round(avg_confidence, 3),
            "learning_cases": learning_cases,
        }

    def delete_case(self, case_id: str) -> bool:
        """
        Remove um caso (para testes/desenvolvimento).
        Em produção, seria marcação como deleted ao invés de exclusão.
        """
        if case_id in self._cases_store:
            del self._cases_store[case_id]
            return True
        return False
