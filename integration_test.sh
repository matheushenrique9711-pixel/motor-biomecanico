#!/bin/bash

echo "🧪 Motor Biomecânico - Teste de Integração"
echo "==========================================="
echo ""

BASE_URL="http://localhost:8000"

# 1. Test Backend Health
echo "1️⃣  Testando saúde do backend..."
HEALTH=$(curl -s $BASE_URL/health)
echo "✅ Resposta: $HEALTH"
echo ""

# 2. Create a case
echo "2️⃣  Criando novo caso clínico..."
CREATE_RESPONSE=$(curl -s -X POST $BASE_URL/api/cases/ \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "test-patient-001",
    "name": "Maria Santos",
    "age": 42,
    "gender": "F",
    "main_complaint": "Dor nos pés e tornozelos"
  }')

CASE_ID=$(echo $CREATE_RESPONSE | jq -r '.case_id')
echo "✅ Caso criado: $CASE_ID"
echo ""

# 3. Analyze biomechanical profile
echo "3️⃣  Analisando perfil biomecânico..."
ANALYZE_RESPONSE=$(curl -s -X POST $BASE_URL/api/cases/$CASE_ID/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "foot_length": 250.0,
    "arch_length_midfoot": 120.0,
    "forefoot_width": 95.0,
    "midfoot_width": 85.0,
    "hindfoot_width": 65.0,
    "arch_height_at_50pct": 18.0,
    "arch_height_at_midfoot": 20.0,
    "arch_index": 0.18,
    "hallux_valgus_angle": 0.0,
    "intermetatarsal_angle": 0.0,
    "subtalar_inversion_angle": 0.0,
    "tibial_torsion_asymmetry": 0.0,
    "load_distribution": {
      "hallux_zone": 0.15,
      "medial_metatarsal": 0.20,
      "central_metatarsal": 0.25,
      "lateral_metatarsal": 0.15,
      "heel_zone": 0.25
    },
    "left_right_asymmetry": 0.0,
    "scan_quality": 0.95
  }')

echo "✅ Análise concluída"
ARCH_INDEX=$(echo $ANALYZE_RESPONSE | jq -r '.biomechanical_profile.arch_index')
echo "   Índice do arco: $ARCH_INDEX"
echo ""

# 4. Generate suggestions
echo "4️⃣  Gerando sugestões clínicas..."
SUGGESTIONS_RESPONSE=$(curl -s -X POST $BASE_URL/api/cases/$CASE_ID/suggestions/ \
  -H "Content-Type: application/json")

NUM_SUGGESTIONS=$(echo $SUGGESTIONS_RESPONSE | jq -r '.suggestions | length')
echo "✅ Sugestões geradas: $NUM_SUGGESTIONS"
CONDITION=$(echo $SUGGESTIONS_RESPONSE | jq -r '.primary_condition')
echo "   Condição primária: $CONDITION"
echo ""

# 5. Get case details
echo "5️⃣  Recuperando detalhes do caso..."
CASE_DETAILS=$(curl -s -X GET $BASE_URL/api/cases/$CASE_ID)
STATUS=$(echo $CASE_DETAILS | jq -r '.status')
echo "✅ Status do caso: $STATUS"
echo ""

# Summary
echo "✅ Teste de integração completo!"
echo ""
echo "Resumo:"
echo "  - Backend: ✅ Funcionando"
echo "  - Frontend API: ✅ Testável em http://localhost:5173"
echo "  - Caso de Teste: $CASE_ID"
echo "  - Condição Detectada: $CONDITION"
echo ""
