"""
Modelos de parâmetros da palmilha.
Controles paramétricos que definem a geometria completa.
"""

from pydantic import BaseModel, Field
from typing import Dict, Tuple, Optional


class InsoleParameter(BaseModel):
    """Um parâmetro individual da palmilha com limites."""

    name: str = Field(..., description="Nome do parâmetro")
    value: float = Field(..., description="Valor atual")
    min_value: float = Field(..., description="Valor mínimo seguro")
    max_value: float = Field(..., description="Valor máximo seguro")
    unit: str = Field(default="mm", description="Unidade (mm, graus, adim)")
    description: str = Field(default="", description="Descrição do parâmetro")
    uncommon_threshold: Optional[float] = Field(default=None, description="Valor acima do qual é 'incomum'")

    def is_valid(self) -> bool:
        """Valida se valor está dentro dos limites seguros."""
        return self.min_value <= self.value <= self.max_value

    def is_uncommon(self) -> bool:
        """Verifica se o valor é incomum (requer confirmação)."""
        if self.uncommon_threshold is None:
            return False
        return self.value > self.uncommon_threshold

    def clip_to_safe_range(self) -> float:
        """Força o valor para o intervalo seguro."""
        return max(self.min_value, min(self.max_value, self.value))


class InsoleParameterSet(BaseModel):
    """
    Conjunto completo de parâmetros que controlam a geometria da palmilha.
    Cada parâmetro é contínuo e afeta a forma final.
    """

    # ========== ESPESSURA GERAL ==========
    base_thickness_mm: float = Field(
        default=4.5,
        ge=3, le=6,
        description="Espessura base da palmilha (mm)"
    )

    # ========== ARCO MEDIAL ==========
    arch_height_medial: float = Field(
        default=0.0,
        ge=0, le=12,
        description="Elevação do arco medial (mm)"
    )

    arch_height_lateral: float = Field(
        default=0.0,
        ge=0, le=6,
        description="Elevação do arco lateral (mm)"
    )

    arch_transition_smoothness: float = Field(
        default=1.0,
        ge=0, le=1,
        description="Suavidade da transição do arco (0=abrupta, 1=suave)"
    )

    # ========== INCLINAÇÕES ==========
    medial_incline_angle: float = Field(
        default=0.0,
        ge=-5, le=15,
        description="Inclinação medial (graus)"
    )

    lateral_incline_angle: float = Field(
        default=0.0,
        ge=-10, le=5,
        description="Inclinação lateral (graus)"
    )

    # ========== CALCÂNEO ==========
    heel_cup_depth_mm: float = Field(
        default=0.0,
        ge=0, le=6,
        description="Profundidade da cúpula calcanear (mm)"
    )

    heel_cup_width_percent: float = Field(
        default=100.0,
        ge=80, le=120,
        description="Largura relativa da cúpula (%)"
    )

    heel_unloading_mm: float = Field(
        default=0.0,
        ge=0, le=8,
        description="Recesso no calcâneo para alívio (mm)"
    )

    # ========== ANTEPÉ ==========
    metatarsal_dome_height: float = Field(
        default=0.0,
        ge=0, le=8,
        description="Altura da cúpula metatarsal (mm)"
    )

    forefoot_rocker_radius: float = Field(
        default=25.0,
        ge=15, le=40,
        description="Raio do rocker do antepé (mm)"
    )

    mt1_dome_height: float = Field(
        default=0.0,
        ge=0, le=6,
        description="Altura específica da cúpula MT1 (mm)"
    )

    mt1_medial_extension: float = Field(
        default=0.0,
        ge=0, le=10,
        description="Extensão medial do MT1 (mm)"
    )

    # ========== CUNHAS ==========
    lateral_wedge_angle: float = Field(
        default=0.0,
        ge=0, le=10,
        description="Ângulo da cunha lateral (graus)"
    )

    # ========== RIGIDEZ REGIONAL ==========
    medial_arch_stiffness: float = Field(
        default=1.0,
        ge=0.8, le=1.6,
        description="Multiplicador de rigidez do arco medial"
    )

    forefoot_stiffness: float = Field(
        default=1.0,
        ge=0.8, le=1.5,
        description="Multiplicador de rigidez do antepé"
    )

    # ========== ALÍVIOS LOCALIZADOS ==========
    plantar_fascia_relief: float = Field(
        default=0.0,
        ge=0, le=3,
        description="Reforço fascial/alívio (mm)"
    )

    morton_neuroma_relief_mm: float = Field(
        default=0.0,
        ge=0, le=4,
        description="Recesso para neuroma de Morton (mm)"
    )

    bunion_relief_depth: float = Field(
        default=0.0,
        ge=-4, le=0,
        description="Recesso MT1 lateral para joanete (mm)"
    )

    # ========== ACABAMENTO ==========
    surface_texture: str = Field(
        default="smooth",
        description="Textura da superfície (smooth/dimpled/textured)"
    )

    edge_radius_mm: float = Field(
        default=1.5,
        ge=1, le=3,
        description="Raio de arredondamento das bordas (mm)"
    )

    def validate(self) -> Tuple[bool, list]:
        """
        Valida se todos os parâmetros estão dentro dos limites.
        Returns: (is_valid, list_of_warnings)
        """
        warnings = []

        # Validações básicas de intervalo
        if self.arch_height_medial > 12:
            warnings.append("Arco medial muito elevado (>12mm)")

        if self.lateral_wedge_angle > 8:
            warnings.append("Cunha lateral acima do recomendado (>8°)")

        if (self.heel_unloading_mm + self.heel_cup_depth_mm) > 10:
            warnings.append("Alívio calcanear total muito agressivo (>10mm)")

        if self.metatarsal_dome_height > 6:
            warnings.append("Cúpula metatarsal muito alta (>6mm)")

        # Validações de coerência
        if self.is_cavusfoot_configuration() and self.arch_height_medial > 2:
            warnings.append("Configuração cava: arco já elevado, aumentar pode causar problemas")

        if (self.medial_arch_stiffness < 1.0 and self.arch_height_medial > 5):
            warnings.append("Arco alto com rigidez baixa: pode flectir excessivamente")

        return len(warnings) == 0, warnings

    def is_cavusfoot_configuration(self) -> bool:
        """Detecta se a configuração é para pé cavo."""
        return self.medial_incline_angle > 5 and self.lateral_wedge_angle < 2

    def is_flatfoot_configuration(self) -> bool:
        """Detecta se a configuração é para pé plano."""
        return self.arch_height_medial > 3 and self.lateral_wedge_angle > 3

    def is_hallux_valgus_configuration(self) -> bool:
        """Detecta se a configuração trata hálux valgo."""
        return self.mt1_dome_height > 1 or self.bunion_relief_depth < -1

    def dict_for_geometry(self) -> dict:
        """Retorna parâmetros formatados para gerador 3D."""
        return {
            "base_thickness_mm": self.base_thickness_mm,
            "arch_height_medial": self.arch_height_medial,
            "arch_height_lateral": self.arch_height_lateral,
            "arch_transition_smoothness": self.arch_transition_smoothness,
            "medial_incline_angle": self.medial_incline_angle,
            "lateral_incline_angle": self.lateral_incline_angle,
            "heel_cup_depth_mm": self.heel_cup_depth_mm,
            "heel_cup_width_percent": self.heel_cup_width_percent,
            "heel_unloading_mm": self.heel_unloading_mm,
            "metatarsal_dome_height": self.metatarsal_dome_height,
            "forefoot_rocker_radius": self.forefoot_rocker_radius,
            "mt1_dome_height": self.mt1_dome_height,
            "mt1_medial_extension": self.mt1_medial_extension,
            "lateral_wedge_angle": self.lateral_wedge_angle,
            "medial_arch_stiffness": self.medial_arch_stiffness,
            "forefoot_stiffness": self.forefoot_stiffness,
            "morton_neuroma_relief_mm": self.morton_neuroma_relief_mm,
            "bunion_relief_depth": self.bunion_relief_depth,
            "edge_radius_mm": self.edge_radius_mm,
        }

    class Config:
        json_schema_extra = {
            "example": {
                "base_thickness_mm": 4.5,
                "arch_height_medial": 0.0,
                "arch_height_lateral": 0.0,
                "heel_cup_depth_mm": 0.0,
                "metatarsal_dome_height": 0.0,
                "lateral_wedge_angle": 0.0,
            }
        }
