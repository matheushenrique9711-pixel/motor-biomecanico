-- Seed foot condition presets
-- These are pre-configured templates for common foot conditions

INSERT INTO foot_condition_presets (
    condition_name,
    description,
    severity_level,
    clinical_indicators,
    common_complaints,
    recommended_parameters,
    arch_support_level,
    heel_height_mm,
    material_recommendation,
    created_at
) VALUES

-- PÉ CAVO (High Arch)
(
    'Pé Cavo',
    'Arco plantar muito elevado, causando distribuição irregular de carga. Comum em atletas e pode causar dor no calcanhar e na bola do pé.',
    'leve',
    '["arco muito elevado", "contato limitado com o solo", "distribuição de carga concentrada", "possível inversão do tornozelo"]',
    '["dor no calcanhar", "dor na bola do pé", "instabilidade lateral", "fadiga dos pés após atividade"]',
    '{"arch_height_medial": 28.0, "heel_height": 10.0, "material": "EVA", "density": 0.95, "forefoot_thickness": 5.0, "midfoot_thickness": 4.0, "heel_thickness": 8.0, "lateral_support": "alto", "metatarsal_padding": 6.0}',
    'alto',
    10.0,
    'EVA com suporte lateral reforçado',
    NOW()
),

-- PÉ PLANO LEVE (Flat Foot - Mild)
(
    'Pé Plano Leve',
    'Arco plantar parcialmente desabado com contato aumentado do arco com o solo. Pode causar fadiga e dor com uso prolongado.',
    'leve',
    '["arco reduzido", "contato aumentado com solo", "pronação leve", "distribuição de carga alterada"]',
    '["fadiga no pé após atividade", "dor no arco", "inchaço leve ao final do dia", "desconforto ao caminhar"]',
    '{"arch_height_medial": 18.0, "heel_height": 12.0, "material": "poliuretano", "density": 1.1, "forefoot_thickness": 4.5, "midfoot_thickness": 3.5, "heel_thickness": 7.0, "medial_support": "médio", "contour_arch": true}',
    'médio',
    12.0,
    'Poliuretano com suporte medial customizado',
    NOW()
),

-- PÉ PLANO MODERADO (Flat Foot - Moderate)
(
    'Pé Plano Moderado',
    'Arco plantar significativamente desabado com contato substancial com o solo. Causa dor notável e afeta a marcha.',
    'moderada',
    '["arco muito reduzido", "contato significativo com solo", "pronação moderada", "deformidade visível", "instabilidade medial"]',
    '["dor no arco plantar", "dor no calcanhar", "inchaço e dor após atividade", "dificuldade em caminhar por tempo prolongado", "dor nos joelhos"]',
    '{"arch_height_medial": 14.0, "heel_height": 14.0, "material": "poliuretano", "density": 1.2, "forefoot_thickness": 5.0, "midfoot_thickness": 4.0, "heel_thickness": 8.5, "medial_support": "alto", "contour_arch": true, "heel_cup": "profundo", "lateral_wedge": 3.0}',
    'alto',
    14.0,
    'Poliuretano rígido com suporte medial forte',
    NOW()
),

-- PÉ PLANO SEVERO (Flat Foot - Severe)
(
    'Pé Plano Severo',
    'Colapso completo ou quase completo do arco plantar. Requer suporte substancial e pode estar associado a outras condições.',
    'severa',
    '["arco colapsado completamente", "contato total do arco com solo", "pronação severa", "deformidade significativa", "instabilidade severa", "possível rigidez da articulação"]',
    '["dor severa no arco", "dor severa no calcanhar", "dor nos joelhos e quadril", "dificuldade significativa em caminhar", "inchaço frequente", "impossibilidade de atividades intensas"]',
    '{"arch_height_medial": 10.0, "heel_height": 16.0, "material": "poliuretano", "density": 1.3, "forefoot_thickness": 6.0, "midfoot_thickness": 5.0, "heel_thickness": 10.0, "medial_support": "máximo", "contour_arch": true, "heel_cup": "profundo", "lateral_wedge": 5.0, "rigid_shank": true}',
    'máximo',
    16.0,
    'Poliuretano rígido com estrutura de reforço',
    NOW()
),

-- JOANETE (Hallux Valgus)
(
    'Joanete (Hallux Valgus)',
    'Desvio lateral do primeiro dedo (hálux) em relação ao primeiro metatarso. Causa dor e desconforto ao usar calçados.',
    'moderada',
    '["desvio do hálux", "saliência medial", "ângulo de valgus aumentado", "contato com calçado irritado", "possível sobreposição dos dedos"]',
    '["dor ao lado do dedão", "inchaço local", "dificuldade em usar sapatos", "dor ao caminhar", "vermelhidão na saliência"]',
    '{"arch_height_medial": 20.0, "heel_height": 12.0, "material": "poliuretano", "density": 1.1, "forefoot_thickness": 5.5, "midfoot_thickness": 3.5, "heel_thickness": 7.0, "hallux_relief": true, "hallux_relief_width": 12.0, "extra_padding_region": "medial_forefoot"}',
    'médio',
    12.0,
    'Poliuretano com alívio customizado para hálux',
    NOW()
),

-- METATARSALGIA (Ball of Foot Pain)
(
    'Metatarsalgia',
    'Dor sob os metatarsos, geralmente na região anterior do pé. Causada por distribuição inadequada de carga ou pressão excessiva.',
    'moderada',
    '["pressão aumentada sob metatarsos", "calos ou hiperqueratose", "inflamação local", "distribuição de carga alterada"]',
    '["dor na bola do pé", "sensação de queimação", "dor ao estar em pé por tempo prolongado", "piora com atividade intensa"]',
    '{"arch_height_medial": 19.0, "heel_height": 11.0, "material": "EVA", "density": 0.9, "forefoot_thickness": 6.5, "midfoot_thickness": 3.5, "heel_thickness": 7.0, "metatarsal_padding": 8.0, "metatarsal_bar": true, "pressure_relief_pattern": "anterior"}',
    'médio',
    11.0,
    'EVA com acolchoamento metatarsal especial',
    NOW()
),

-- FASCITE PLANTAR (Plantar Fasciitis)
(
    'Fascite Plantar',
    'Inflamação do tecido fibroso (fáscia) na sola do pé. Causa dor no calcanhar, especialmente ao primeiro passo da manhã.',
    'moderada',
    '["inflamação da fáscia plantar", "dor no calcanhar", "rigidez matinal", "piora com atividade", "possível calcificação do calcanhar"]',
    '["dor severa no calcanhar ao acordar", "dor ao caminhar", "dor que melhora com repouso", "sensibilidade no arco plantar"]',
    '{"arch_height_medial": 21.0, "heel_height": 13.0, "material": "poliuretano", "density": 1.1, "forefoot_thickness": 4.5, "midfoot_thickness": 3.5, "heel_thickness": 9.0, "heel_cup": "profundo", "arch_support": "médio-alto", "shock_absorption": "máxima"}',
    'médio-alto',
    13.0,
    'Poliuretano com absorção de choque e suporte',
    NOW()
),

-- DEDOS EM GARRA (Claw Toes)
(
    'Dedos em Garra',
    'Flexão anormal dos dedos deixando-os em formato de garra. Causa pressão aumentada e dor sobre os dedos.',
    'moderada',
    '["flexão dos dedos em garra", "calos no dorso dos dedos", "pressão aumentada", "desalinhamento progressivo"]',
    '["dor no dorso dos dedos", "dificuldade em encontrar calçado confortável", "calos ou calosidades", "dor ao caminhar"]',
    '{"arch_height_medial": 19.0, "heel_height": 11.0, "material": "EVA", "density": 0.9, "forefoot_thickness": 6.0, "midfoot_thickness": 3.5, "heel_thickness": 7.0, "toe_box_padding": true, "total_contact_design": true}',
    'médio',
    11.0,
    'EVA com design de contato total e acolchoamento',
    NOW()
),

-- PÉ DIABÉTICO (Diabetic Foot)
(
    'Pé Diabético',
    'Condição que requer cuidados especiais devido a sensibilidade reduzida e cicatrização lenta. Prevenção de úlceras é crítica.',
    'severa',
    '["neuropatia periférica", "sensibilidade reduzida", "cicatrização lenta", "risco de úlceras", "possível deformidade"]',
    '["dormência nos pés", "formigamento", "feridas que não cicatrizam bem", "desconforto ao caminhar"]',
    '{"arch_height_medial": 17.0, "heel_height": 12.0, "material": "poliuretano", "density": 1.0, "forefoot_thickness": 6.5, "midfoot_thickness": 4.0, "heel_thickness": 9.0, "total_contact_design": true, "seamless_construction": true, "pressure_distribution": "uniforme", "cushioning": "máxima"}',
    'alto',
    12.0,
    'Poliuretano com design total contact e costura mínima',
    NOW()
),

-- PÉ DE ATLETA (High-Performance)
(
    'Pé de Atleta - Alto Desempenho',
    'Palmilha otimizada para atletas buscando performance máxima, com suporte dinâmico e absorção de choque.',
    'leve',
    '["carga dinâmica elevada", "necessidade de estabilidade", "demanda por desempenho máximo", "impacto aumentado"]',
    '["nenhuma dor em condições normais", "desejo de melhor performance", "busca por máxima estabilidade", "interesse em reduzir fadiga"]',
    '{"arch_height_medial": 22.0, "heel_height": 10.0, "material": "poliuretano", "density": 1.15, "forefoot_thickness": 4.5, "midfoot_thickness": 3.0, "heel_thickness": 6.5, "shock_absorption": "alto", "lateral_stability": "máxima", "responsive_cushioning": true}',
    'alto',
    10.0,
    'Poliuretano com tecnologia de resposta dinâmica',
    NOW()
);

-- Verificar inserção
SELECT COUNT(*) as total_presets FROM foot_condition_presets;
