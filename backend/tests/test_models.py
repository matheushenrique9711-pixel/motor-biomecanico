"""
Testes básicos para validação dos modelos de dados.
Garante que os modelos funcionam corretamente.
"""

import pytest
from app.models import (
    BiomechanicalFootProfile,
    LoadDistribution,
    InsoleParameterSet,
    ClinicalCase,
    PatientInfo,
    ClinicalRule,
    ConditionType,
)


class TestBiomechanicalModels:
    """Testes para modelos biomecânicos."""

    def test_load_distribution_normalization(self):
        """Testa normalização de distribuição de carga."""
        load = LoadDistribution(
            hallux_zone=0.2,
            medial_metatarsal=0.2,
            central_metatarsal=0.2,
            lateral_metatarsal=0.2,
            heel_zone=0.2,
        )

        # Soma antes de normalizar
        total = (
            load.hallux_zone
            + load.medial_metatarsal
            + load.central_metatarsal
            + load.lateral_metatarsal
            + load.heel_zone
        )
        assert total == 1.0

    def test_biomechanical_flatfoot_detection(self):
        """Testa detecção de pé plano."""
        profile = BiomechanicalFootProfile(
            foot_length=250.0,
            arch_length_midfoot=120.0,
            forefoot_width=95.0,
            midfoot_width=85.0,
            hindfoot_width=65.0,
            arch_height_at_50pct=10.0,
            arch_height_at_midfoot=12.0,
            arch_index=0.18,  # < 0.21 = flatfoot
            load_distribution=LoadDistribution(
                hallux_zone=0.15,
                medial_metatarsal=0.20,
                central_metatarsal=0.25,
                lateral_metatarsal=0.15,
                heel_zone=0.25,
            ),
        )

        assert profile.is_flatfoot is True
        assert profile.is_cavusfoot is False

    def test_biomechanical_cavusfoot_detection(self):
        """Testa detecção de pé cavo."""
        profile = BiomechanicalFootProfile(
            foot_length=250.0,
            arch_length_midfoot=120.0,
            forefoot_width=95.0,
            midfoot_width=85.0,
            hindfoot_width=65.0,
            arch_height_at_50pct=35.0,
            arch_height_at_midfoot=37.0,
            arch_index=0.28,  # > 0.26 = cavus
            load_distribution=LoadDistribution(
                hallux_zone=0.15,
                medial_metatarsal=0.20,
                central_metatarsal=0.25,
                lateral_metatarsal=0.15,
                heel_zone=0.25,
            ),
        )

        assert profile.is_cavusfoot is True
        assert profile.is_flatfoot is False

    def test_biomechanical_hallux_valgus_detection(self):
        """Testa detecção de hálux valgo."""
        profile = BiomechanicalFootProfile(
            foot_length=250.0,
            arch_length_midfoot=120.0,
            forefoot_width=95.0,
            midfoot_width=85.0,
            hindfoot_width=65.0,
            arch_height_at_50pct=20.0,
            arch_height_at_midfoot=22.0,
            arch_index=0.16,
            hallux_valgus_angle=18.0,  # > 15 = hallux valgus
            load_distribution=LoadDistribution(
                hallux_zone=0.15,
                medial_metatarsal=0.20,
                central_metatarsal=0.25,
                lateral_metatarsal=0.15,
                heel_zone=0.25,
            ),
        )

        assert profile.has_hallux_valgus is True


class TestInsoleParameters:
    """Testes para parâmetros da palmilha."""

    def test_insole_parameters_validation(self):
        """Testa validação de parâmetros."""
        params = InsoleParameterSet(
            base_thickness_mm=4.5,
            arch_height_medial=6.0,
            metatarsal_dome_height=4.0,
        )

        # Valida se todos os parâmetros estão dentro dos limites
        is_valid, warnings = params.validate()
        assert is_valid is True
        assert len(warnings) == 0

    def test_insole_flatfoot_configuration_detection(self):
        """Testa detecção de configuração para pé plano."""
        params = InsoleParameterSet(
            arch_height_medial=6.0,
            lateral_wedge_angle=0.0,
        )

        # Pé plano: arco alto com cunha baixa
        assert params.is_flatfoot_configuration() is True

    def test_insole_dict_for_geometry(self):
        """Testa conversão para dicionário para gerador 3D."""
        params = InsoleParameterSet()
        geom_dict = params.dict_for_geometry()

        # Verifica que contém os parâmetros esperados
        assert "arch_height_medial" in geom_dict
        assert "base_thickness_mm" in geom_dict
        assert "metatarsal_dome_height" in geom_dict


class TestClinicalModels:
    """Testes para modelos clínicos."""

    def test_clinical_rule_creation(self):
        """Testa criação de regra clínica."""
        rule = ClinicalRule(
            rule_id="TEST_001",
            condition_type=ConditionType.FLATFOOT,
            condition_name="Test Condition",
            detection_criteria="test_criteria",
            parameter_adjustments=[],
            clinical_evidence="Test evidence",
        )

        assert rule.rule_id == "TEST_001"
        assert rule.condition_type == ConditionType.FLATFOOT
        assert rule.confidence_threshold == 0.7  # Default

    def test_clinical_case_creation(self):
        """Testa criação de caso clínico."""
        patient = PatientInfo(
            patient_id="pat-001",
            name="Test Patient",
            age=45,
            gender="M",
            main_complaint="Test complaint",
        )

        case = ClinicalCase(
            case_id="case-001",
            patient=patient,
        )

        assert case.patient.name == "Test Patient"
        assert case.status.value == "created"

    def test_case_ready_for_geometry(self):
        """Testa verificação de prontidão para geometria."""
        patient = PatientInfo(
            patient_id="pat-001",
            name="Test",
            age=45,
            gender="M",
            main_complaint="Test",
        )

        case = ClinicalCase(case_id="case-001", patient=patient)

        # Não pronto sem parâmetros
        assert case.is_ready_for_geometry_generation() is False

        # Pronto com parâmetros
        case.insole_parameters = InsoleParameterSet().dict()
        assert case.is_ready_for_geometry_generation() is True


class TestIntegration:
    """Testes de integração entre camadas."""

    def test_full_workflow(self):
        """Testa fluxo completo: perfil → caso → parâmetros."""
        # 1. Criar perfil biomecânico
        profile = BiomechanicalFootProfile(
            foot_length=250.0,
            arch_length_midfoot=120.0,
            forefoot_width=95.0,
            midfoot_width=85.0,
            hindfoot_width=65.0,
            arch_height_at_50pct=10.0,
            arch_height_at_midfoot=12.0,
            arch_index=0.18,
            load_distribution=LoadDistribution(
                hallux_zone=0.15,
                medial_metatarsal=0.20,
                central_metatarsal=0.25,
                lateral_metatarsal=0.15,
                heel_zone=0.25,
            ),
        )

        assert profile.is_flatfoot is True

        # 2. Criar caso para paciente
        patient = PatientInfo(
            patient_id="pat-001",
            name="João Silva",
            age=45,
            gender="M",
            main_complaint="Dor no arco",
        )

        case = ClinicalCase(
            case_id="case-001",
            patient=patient,
            biomechanical_profile=profile.dict(),
        )

        assert case.primary_condition is None

        # 3. Aplicar parâmetros apropriados para flatfoot
        params = InsoleParameterSet(
            arch_height_medial=6.0,
            medial_arch_stiffness=1.3,
            heel_cup_depth_mm=3.0,
        )

        case.insole_parameters = params.dict()

        # 4. Verificar que está pronto para geometria
        assert case.is_ready_for_geometry_generation() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
