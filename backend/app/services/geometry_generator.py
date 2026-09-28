"""
Gerador de Geometria 3D para Palmilhas Ortopédicas Parametrizadas.
Usa CadQuery para modelagem 3D e exportação STL.
"""

import os
from datetime import datetime
from io import BytesIO
import cadquery as cq
from pathlib import Path


class GeometryGenerator:
    """
    Gera geometria 3D de palmilhas baseada em parâmetros biomecânicos.
    Implementa aleições específicas para diferentes condições clínicas.
    """

    # Parâmetros dimensionais básicos (em mm)
    DEFAULT_PARAMS = {
        'foot_length': 250.0,           # Comprimento do pé
        'foot_width': 95.0,             # Largura da parte frontal
        'thickness_base': 3.0,          # Espessura base da palmilha
        'arch_height_medial': 6.0,      # Altura do arco medial
        'arch_height_lateral': 3.0,     # Altura do arco lateral
        'heel_cup_depth': 3.0,          # Profundidade da cúpula calcanear
        'heel_width': 65.0,             # Largura do calcanhar
        'medial_arch_stiffness': 1.0,   # Rigidez do arco medial
        'lateral_arch_stiffness': 0.8,  # Rigidez do arco lateral
        'forefoot_cushioning': 1.2,     # Amortecimento do antepé
    }

    def __init__(self):
        """Inicializa o gerador de geometria."""
        self.output_dir = Path('/tmp/stl_exports')
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_insole_geometry(
        self,
        case_id: str,
        foot_length: float,
        foot_width: float,
        arch_index: float,
        condition_type: str = 'normal',
        parameters: dict = None,
    ) -> dict:
        """
        Gera geometria 3D de palmilha baseada em parâmetros.

        Args:
            case_id: ID do caso clínico
            foot_length: Comprimento do pé em mm
            foot_width: Largura do pé em mm
            arch_index: Índice do arco (0-1)
            condition_type: Tipo de condição (normal, flatfoot, cavusfoot, etc)
            parameters: Dicionário com parâmetros adicionais

        Returns:
            Dicionário com informações da geometria gerada
        """
        params = self.DEFAULT_PARAMS.copy()
        if parameters:
            params.update(parameters)

        # Ajusta parâmetros conforme a condição
        adjusted_params = self._adjust_parameters_for_condition(
            arch_index, condition_type, params
        )

        # Gera a geometria
        try:
            solid = self._create_base_insole(foot_length, foot_width, adjusted_params)
            solid = self._add_arch_support(solid, adjusted_params)
            solid = self._add_heel_cup(solid, adjusted_params)
            solid = self._add_metatarsal_support(solid, adjusted_params)

            # Exporta para STL
            stl_path = self._export_to_stl(case_id, solid)

            return {
                'success': True,
                'case_id': case_id,
                'stl_path': stl_path,
                'condition': condition_type,
                'arch_index': arch_index,
                'parameters_applied': adjusted_params,
                'generated_at': datetime.now().isoformat(),
                'dimensions': {
                    'length': foot_length,
                    'width': foot_width,
                    'height': adjusted_params['arch_height_medial'] + adjusted_params['thickness_base'],
                },
            }
        except Exception as e:
            return {
                'success': False,
                'case_id': case_id,
                'error': str(e),
                'generated_at': datetime.now().isoformat(),
            }

    def _adjust_parameters_for_condition(
        self, arch_index: float, condition_type: str, params: dict
    ) -> dict:
        """Ajusta parâmetros de acordo com a condição clínica detectada."""
        adjusted = params.copy()

        if condition_type == 'flatfoot':
            # Pé plano: aumenta suporte do arco
            adjusted['arch_height_medial'] = max(6.0, params.get('arch_height_medial', 6.0) * 1.5)
            adjusted['medial_arch_stiffness'] = min(1.6, params.get('medial_arch_stiffness', 1.0) * 1.3)
            adjusted['heel_cup_depth'] = max(3.0, params.get('heel_cup_depth', 3.0) * 1.2)
            adjusted['forefoot_cushioning'] = params.get('forefoot_cushioning', 1.2) * 0.9

        elif condition_type == 'cavusfoot':
            # Pé cavo: reduz arco, aumenta amortecimento
            adjusted['arch_height_medial'] = params.get('arch_height_medial', 6.0) * 0.6
            adjusted['arch_height_lateral'] = params.get('arch_height_lateral', 3.0) * 1.3
            adjusted['forefoot_cushioning'] = params.get('forefoot_cushioning', 1.2) * 1.4
            adjusted['heel_cup_depth'] = params.get('heel_cup_depth', 3.0) * 0.8

        elif condition_type == 'hallux_valgus':
            # Hálux valgo: suporte na articulação do halux
            adjusted['forefoot_cushioning'] = params.get('forefoot_cushioning', 1.2) * 1.1
            adjusted['medial_arch_stiffness'] = params.get('medial_arch_stiffness', 1.0) * 1.4

        elif condition_type == 'excessive_pronation':
            # Pronação excessiva: aumenta suporte medial
            adjusted['arch_height_medial'] = params.get('arch_height_medial', 6.0) * 1.4
            adjusted['medial_arch_stiffness'] = params.get('medial_arch_stiffness', 1.0) * 1.5
            adjusted['heel_cup_depth'] = params.get('heel_cup_depth', 3.0) * 1.3

        elif condition_type == 'metatarsalgia':
            # Metatarsalgia: aumenta amortecimento do antepé
            adjusted['forefoot_cushioning'] = params.get('forefoot_cushioning', 1.2) * 1.5

        return adjusted

    def _create_base_insole(
        self, foot_length: float, foot_width: float, params: dict
    ) -> cq.Workplane:
        """Cria a forma base da palmilha."""
        # Cria forma de pé (aproximação com curvas)
        thickness = params['thickness_base']

        # Base retangular (será arredondada depois)
        base = (
            cq.Workplane('XY')
            .box(foot_length, foot_width, thickness)
            .edges('|Z').fillet(8)  # Arredonda arestas
        )

        return base

    def _add_arch_support(self, insole: cq.Workplane, params: dict) -> cq.Workplane:
        """Adiciona suporte do arco à palmilha."""
        # Cria um sólido adicional para o suporte do arco
        arch_height_medial = params['arch_height_medial']
        arch_height_lateral = params['arch_height_lateral']

        # Suporte medial (área interna do pé)
        medial_arch = (
            cq.Workplane('XY')
            .box(150, 30, arch_height_medial)
            .edges('|Z').fillet(3)
            .translate((0, -20, arch_height_medial / 2))
        )

        # Suporte lateral (área externa do pé)
        lateral_arch = (
            cq.Workplane('XY')
            .box(150, 25, arch_height_lateral)
            .edges('|Z').fillet(3)
            .translate((0, 25, arch_height_lateral / 2))
        )

        # Combina geometrias
        result = insole.union(medial_arch).union(lateral_arch)

        return result

    def _add_heel_cup(self, insole: cq.Workplane, params: dict) -> cq.Workplane:
        """Adiciona cúpula calcanear à palmilha."""
        heel_depth = params['heel_cup_depth']
        heel_width = params['heel_width']

        # Cria uma reentrância para o calcanhar
        heel_cup = (
            cq.Workplane('XY')
            .sphere(heel_depth * 1.5)
            .scale(1.0, heel_width / (heel_depth * 3), 0.8)
            .translate((0, -params['foot_length'] / 2.5, 0))
        )

        # Subtrai a forma do calcanhar
        result = insole.cut(heel_cup)

        return result

    def _add_metatarsal_support(self, insole: cq.Workplane, params: dict) -> cq.Workplane:
        """Adiciona suporte metatársico (antepé)."""
        cushioning = params['forefoot_cushioning']

        # Cria suporte nas 5 zonas metatársicas
        metatarsal_heights = [
            1.5 * cushioning,  # Hálux
            2.0 * cushioning,  # Metatarsal 2
            2.0 * cushioning,  # Metatarsal 3
            1.8 * cushioning,  # Metatarsal 4
            1.5 * cushioning,  # Metatarsal 5
        ]

        # Cria pequenas elevações para distribuição de carga
        support = None
        zone_width = 18
        start_y = 50

        for i, height in enumerate(metatarsal_heights):
            zone = (
                cq.Workplane('XY')
                .box(zone_width, 40, height)
                .edges('|Z').fillet(1)
                .translate((
                    -36 + i * zone_width,
                    start_y,
                    height / 2
                ))
            )
            support = zone if support is None else support.union(zone)

        result = insole.union(support) if support else insole

        return result

    def _export_to_stl(self, case_id: str, solid: cq.Workplane) -> str:
        """Exporta a geometria para arquivo STL."""
        # Cria filename com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'insole_{case_id}_{timestamp}.stl'
        filepath = self.output_dir / filename

        try:
            # Exporta para STL
            solid.val().exportStl(str(filepath))

            # Verifica se o arquivo foi criado
            if filepath.exists():
                return str(filepath)
            else:
                raise FileNotFoundError(f"Falha ao exportar STL: {filepath}")

        except Exception as e:
            raise Exception(f"Erro ao exportar STL: {str(e)}")

    def get_stl_file(self, case_id: str) -> tuple[bytes, str]:
        """
        Recupera arquivo STL gerado.

        Returns:
            Tupla (bytes, filename)
        """
        stl_files = list(self.output_dir.glob(f'insole_{case_id}_*.stl'))

        if not stl_files:
            raise FileNotFoundError(f"Nenhum arquivo STL encontrado para caso {case_id}")

        # Retorna o arquivo mais recente
        latest_file = max(stl_files, key=lambda p: p.stat().st_mtime)

        with open(latest_file, 'rb') as f:
            return f.read(), latest_file.name

    def delete_stl_file(self, case_id: str) -> bool:
        """Deleta arquivo STL de um caso."""
        stl_files = list(self.output_dir.glob(f'insole_{case_id}_*.stl'))

        for file in stl_files:
            file.unlink()

        return len(stl_files) > 0
