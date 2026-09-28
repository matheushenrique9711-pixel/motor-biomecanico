"""
Modelos de dados biomecânicos do pé.
Estruturas que representam parâmetros extraídos da digitalização.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class FootType(str, Enum):
    """Tipos de pé detectados."""
    FLAT = "flat"
    NORMAL = "normal"
    CAVUS = "cavus"
    VARUS = "varus"
    VALGUS = "valgus"
    MIXED = "mixed"


class AgeGroup(str, Enum):
    """Grupos etários."""
    PEDIATRIC = "pediatric"
    ADULT = "adult"
    ELDERLY = "elderly"


class ActivityLevel(str, Enum):
    """Níveis de atividade."""
    SEDENTARY = "sedentary"
    NORMAL = "normal"
    ATHLETIC = "athletic"


class LoadDistribution(BaseModel):
    """Distribuição de carga em 5 zonas plantares (0-1, somam 1.0)."""

    hallux_zone: float = Field(..., ge=0, le=1, description="Zona do hálux (MT1)")
    medial_metatarsal: float = Field(..., ge=0, le=1, description="MT2-3 mediais")
    central_metatarsal: float = Field(..., ge=0, le=1, description="MT3-4 centrais")
    lateral_metatarsal: float = Field(..., ge=0, le=1, description="MT5 lateral")
    heel_zone: float = Field(..., ge=0, le=1, description="Calcâneo")

    def normalize(self):
        """Normaliza distribuição para soma = 1.0."""
        total = (self.hallux_zone + self.medial_metatarsal +
                 self.central_metatarsal + self.lateral_metatarsal + self.heel_zone)
        if total > 0:
            self.hallux_zone /= total
            self.medial_metatarsal /= total
            self.central_metatarsal /= total
            self.lateral_metatarsal /= total
            self.heel_zone /= total

    def dict_normalized(self) -> dict:
        """Retorna dicionário normalizado."""
        self.normalize()
        return {
            "hallux_zone": self.hallux_zone,
            "medial_metatarsal": self.medial_metatarsal,
            "central_metatarsal": self.central_metatarsal,
            "lateral_metatarsal": self.lateral_metatarsal,
            "heel_zone": self.heel_zone,
        }


class BiomechanicalFootProfile(BaseModel):
    """
    Perfil biomecânico completo do pé extraído de digitalização.
    Todos os valores em mm, ângulos em graus.
    """

    # Medidas longitudinais
    foot_length: float = Field(..., gt=0, description="Comprimento total (mm)")
    arch_length_midfoot: float = Field(..., gt=0, description="Distância calcâneo-arco (mm)")

    # Medidas transversais
    forefoot_width: float = Field(..., gt=0, description="Largura antepé (mm)")
    midfoot_width: float = Field(..., gt=0, description="Largura mediopé (mm)")
    hindfoot_width: float = Field(..., gt=0, description="Largura retropé (mm)")

    # Altura do arco
    arch_height_at_50pct: float = Field(..., ge=0, description="Altura máx arco a 50% (mm)")
    arch_height_at_midfoot: float = Field(..., ge=0, description="Altura arco em Lisfranc (mm)")

    # Índices derivados
    arch_index: float = Field(..., ge=0, description="Índice do arco (altura/(length/2))")

    # Alinhamento e eixos
    hallux_valgus_angle: float = Field(default=0, description="Ângulo hálux (varus=-, valgus=+, graus)")
    intermetatarsal_angle: float = Field(default=0, description="Ângulo MT1-MT2 (graus)")

    # Padrões globais
    subtalar_inversion_angle: float = Field(default=0, description="Pronação=-, Supinação=+ (graus)")
    tibial_torsion_asymmetry: float = Field(default=0, description="Assimetria tíbias (graus)")

    # Distribuição de carga
    load_distribution: LoadDistribution = Field(..., description="Carga em 5 zonas")

    # Assimetrias
    left_right_asymmetry: float = Field(default=0, ge=0, le=1, description="Índice assimetria pés")

    # Metadados
    foot_type: FootType = Field(default=FootType.NORMAL, description="Tipo de pé detectado")
    age_group: AgeGroup = Field(default=AgeGroup.ADULT, description="Grupo etário")
    activity_level: ActivityLevel = Field(default=ActivityLevel.NORMAL, description="Nível atividade")

    # Rastreamento
    scan_quality: float = Field(default=0.95, ge=0, le=1, description="Qualidade da digitalização")

    class Config:
        json_schema_extra = {
            "example": {
                "foot_length": 250.0,
                "arch_length_midfoot": 120.0,
                "forefoot_width": 95.0,
                "midfoot_width": 85.0,
                "hindfoot_width": 65.0,
                "arch_height_at_50pct": 20.0,
                "arch_height_at_midfoot": 22.0,
                "arch_index": 0.16,
                "hallux_valgus_angle": 12.0,
                "intermetatarsal_angle": 9.0,
                "subtalar_inversion_angle": -15.0,
                "tibial_torsion_asymmetry": 0.0,
                "load_distribution": {
                    "hallux_zone": 0.15,
                    "medial_metatarsal": 0.20,
                    "central_metatarsal": 0.25,
                    "lateral_metatarsal": 0.15,
                    "heel_zone": 0.25
                },
                "left_right_asymmetry": 0.05,
                "foot_type": "flat",
                "age_group": "adult",
                "activity_level": "normal",
                "scan_quality": 0.95
            }
        }

    @property
    def is_flatfoot(self) -> bool:
        """Detecta pé plano (arch_index < 0.21)."""
        return self.arch_index < 0.21

    @property
    def is_cavusfoot(self) -> bool:
        """Detecta pé cavo (arch_index > 0.26)."""
        return self.arch_index > 0.26

    @property
    def is_pronated(self) -> bool:
        """Detecta pronação excessiva (ângulo < -8°)."""
        return self.subtalar_inversion_angle < -8

    @property
    def is_supinated(self) -> bool:
        """Detecta supinação excessiva (ângulo > 8°)."""
        return self.subtalar_inversion_angle > 8

    @property
    def has_hallux_valgus(self) -> bool:
        """Detecta hálux valgo (ângulo > 15°)."""
        return self.hallux_valgus_angle > 15
