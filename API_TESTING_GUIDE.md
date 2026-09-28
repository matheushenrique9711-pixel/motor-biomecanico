# Motor Biomecânico - API Testing Guide

Complete guide for testing the integrated database + API layer after Phase 5.

## Quick Start

### Prerequisites
- Docker and docker-compose installed
- `curl` command-line tool or Postman
- PostgreSQL 16 running (via docker-compose)

### Start Services

```bash
cd motor-biomecanico

# Optional: set custom database password
export DB_PASSWORD=your_secure_password

# Start all services
docker-compose up -d

# Check services are running
docker-compose ps

# Verify API health
curl http://localhost:8000/api/health
```

### Check Database Initialization

```bash
# View logs to confirm database initialized
docker-compose logs backend

# Should show:
# ✓ Database initialization successful
# ✓ Database healthy
```

## Complete Workflow Test

This tests the full case lifecycle with database persistence.

### Step 1: Create a Case

```bash
curl -X POST http://localhost:8000/api/cases/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "age": 45,
    "gender": "M",
    "main_complaint": "Dor nos pés",
    "medical_history": "Sem histórico relevante",
    "phone": "(11) 98765-4321",
    "email": "joao@email.com"
  }'
```

**Expected Response:**
```json
{
  "case_id": "CASE-550e8400-e29b-41d4-a716-446655440000",
  "patient_id": "b6a5e7c8-2f1d-4e9a-b8c2-d3e4f5a6b7c8",
  "patient_name": "João Silva",
  "status": "CREATED",
  "created_at": "2026-09-28T13:46:00.000000",
  "id": "f4d3e2c1-b0a9-4f8e-7d6c-5b4a3e2d1c0b"
}
```

Save the `case_id` for the following requests.

### Step 2: Analyze the Case (Biomechanical Analysis)

```bash
CASE_ID="CASE-550e8400-e29b-41d4-a716-446655440000"

curl -X POST http://localhost:8000/api/cases/${CASE_ID}/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "foot_length": 265.0,
    "arch_length_midfoot": 125.0,
    "forefoot_width": 98.0,
    "midfoot_width": 88.0,
    "hindfoot_width": 68.0,
    "arch_height_at_50pct": 22.0,
    "arch_height_at_midfoot": 24.0,
    "arch_index": 0.18,
    "hallux_valgus_angle": 5.0,
    "intermetatarsal_angle": 8.0,
    "subtalar_inversion_angle": 0.0,
    "tibial_torsion_asymmetry": 2.0,
    "load_distribution": {
      "hallux_zone": 0.15,
      "medial_metatarsal": 0.20,
      "central_metatarsal": 0.25,
      "lateral_metatarsal": 0.15,
      "heel_zone": 0.25
    },
    "left_right_asymmetry": 0.05,
    "scan_quality": 0.92
  }'
```

**Expected Response:**
```json
{
  "case_id": "CASE-550e8400-e29b-41d4-a716-446655440000",
  "status": "ANALYZED",
  "biomechanical_profile": { /* full profile data */ },
  "conditions_detected": [],
  "analysis_confidence": 0.85,
  "next_steps": [
    "Revisar análise",
    "Gerar sugestões clínicas",
    "Confirmar ajustes"
  ]
}
```

### Step 3: Generate AI Suggestions

```bash
curl -X POST http://localhost:8000/api/cases/${CASE_ID}/suggestions \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "case_id": "CASE-550e8400-e29b-41d4-a716-446655440000",
  "status": "SUGGESTIONS_GENERATED",
  "suggestions_count": 3,
  "suggestions": [
    {
      "condition": "Pé Plano Leve",
      "recommendation": "Aumentar suporte do arco",
      "severity_level": "leve",
      "parameter_adjustments": [ /* adjustments */ ]
    },
    /* ... more suggestions ... */
  ],
  "primary_condition": "Pé Plano Leve"
}
```

### Step 4: Confirm Suggestions

```bash
curl -X POST http://localhost:8000/api/cases/${CASE_ID}/confirm-suggestions \
  -H "Content-Type: application/json" \
  -d '{
    "clinician_id": "CLI-001",
    "clinician_notes": "Análise concordada, proceeder com fabricação"
  }'
```

**Expected Response:**
```json
{
  "case_id": "CASE-550e8400-e29b-41d4-a716-446655440000",
  "status": "SUGGESTIONS_REVIEWED",
  "message": "Sugestões confirmadas com sucesso"
}
```

### Step 5: Apply Adjustments

```bash
curl -X POST http://localhost:8000/api/cases/${CASE_ID}/apply-adjustments \
  -H "Content-Type: application/json" \
  -d '{
    "insole_parameters": {
      "arch_height_medial": 20.0,
      "heel_height": 12.0,
      "material": "EVA",
      "density": 0.95,
      "forefoot_thickness": 4.0,
      "midfoot_thickness": 3.5,
      "heel_thickness": 6.0
    },
    "modified_by_clinician": true,
    "clinician_id": "CLI-001",
    "clinician_notes": "Ajustado para melhor conforto conforme feedback"
  }'
```

**Expected Response:**
```json
{
  "case_id": "CASE-550e8400-e29b-41d4-a716-446655440000",
  "status": "ADJUSTMENTS_CONFIRMED",
  "insole_parameters": { /* parameters */ },
  "modified_by_clinician": true,
  "message": "Parâmetros aplicados com sucesso"
}
```

### Step 6: Generate 3D Geometry

```bash
curl -X POST http://localhost:8000/api/cases/${CASE_ID}/generate-geometry \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "case_id": "CASE-550e8400-e29b-41d4-a716-446655440000",
  "success": true,
  "stl_file_path": "/tmp/stl_exports/CASE-550e8400-e29b-41d4-a716-446655440000.stl",
  "condition": "Pé Plano Leve",
  "arch_index": 0.18,
  "dimensions": {
    "length": 265.0,
    "width": 98.0,
    "height": 25.0
  },
  "status": "GEOMETRY_GENERATED"
}
```

### Step 7: Export STL File

```bash
curl -X POST http://localhost:8000/api/cases/${CASE_ID}/export-stl \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "case_id": "CASE-550e8400-e29b-41d4-a716-446655440000",
  "filename": "CASE-550e8400-e29b-41d4-a716-446655440000.stl",
  "size_bytes": 245678,
  "status": "EXPORTED",
  "message": "STL pronto para download"
}
```

### Step 8: Add Patient & Clinical Feedback

```bash
curl -X POST http://localhost:8000/api/cases/${CASE_ID}/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "clinical_feedback": "Ótima aceitação pelo paciente, sem queixas",
    "issues": [],
    "patient_feedback": "Muito confortável, sem dor",
    "effectiveness_score": 0.95,
    "comfort_score": 0.92,
    "should_be_learning_case": true
  }'
```

**Expected Response:**
```json
{
  "case_id": "CASE-550e8400-e29b-41d4-a716-446655440000",
  "status": "FEEDBACK_COLLECTED",
  "clinical_feedback": "Ótima aceitação pelo paciente, sem queixas",
  "patient_feedback": "Muito confortável, sem dor",
  "message": "Feedback registrado com sucesso"
}
```

## Query Endpoints

### Get Specific Case

```bash
curl http://localhost:8000/api/cases/${CASE_ID}
```

Returns complete case data with all stored information.

### List All Cases

```bash
curl "http://localhost:8000/api/cases/?limit=50&offset=0"
```

Returns paginated list of all cases.

### List Cases by Status

```bash
curl "http://localhost:8000/api/cases/?status=ANALYZED&limit=50&offset=0"
```

Filters cases by workflow status.

### Get Statistics

```bash
curl http://localhost:8000/api/cases/statistics/summary
```

**Expected Response:**
```json
{
  "total_cases": 3,
  "status_breakdown": {
    "CREATED": 1,
    "ANALYZED": 1,
    "FEEDBACK_COLLECTED": 1
  },
  "condition_breakdown": {
    "Pé Plano Leve": 2,
    "Desconhecida": 1
  },
  "average_confidence": 0.85,
  "cases_with_confidence": 2
}
```

### Get Patient's Cases

```bash
PATIENT_ID="b6a5e7c8-2f1d-4e9a-b8c2-d3e4f5a6b7c8"

curl http://localhost:8000/api/cases/patient/${PATIENT_ID}/cases
```

## Database Verification

### Connect to Database

```bash
# Get PostgreSQL container name
CONTAINER_ID=$(docker ps | grep postgres | awk '{print $1}')

# Connect to database
docker exec -it ${CONTAINER_ID} psql -U motor_user -d motor_biomecanico

# In psql:
\dt                  -- List tables
\d clinical_cases    -- Describe clinical_cases table
SELECT * FROM patients LIMIT 5;
SELECT COUNT(*) FROM clinical_cases;
SELECT status, COUNT(*) FROM clinical_cases GROUP BY status;
```

### Verify Data Persistence

```bash
# Test 1: Data survives restart
docker-compose stop backend
docker-compose start backend

# Query should return same case
curl http://localhost:8000/api/cases/${CASE_ID}

# Test 2: Check audit trail
docker exec -it ${CONTAINER_ID} psql -U motor_user -d motor_biomecanico -c \
  "SELECT * FROM adjustment_history WHERE case_id='${CASE_ID}';"
```

## Health Checks

### API Health

```bash
curl http://localhost:8000/api/health
```

Should return database status.

### Database Health

```bash
# Check via docker-compose
docker-compose ps

# PostgreSQL should show "healthy"
```

## Error Testing

### Test 404 Not Found

```bash
curl http://localhost:8000/api/cases/INVALID-CASE-ID
```

Should return 404 with error message.

### Test Bad Request

```bash
curl -X POST http://localhost:8000/api/cases/${CASE_ID}/analyze \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'
```

Should return 400 with validation error.

### Test Database Error Recovery

```bash
# Stop database
docker-compose stop postgres

# Try API call (should fail gracefully)
curl http://localhost:8000/api/cases/

# Restart database
docker-compose start postgres

# Wait for health check
sleep 10

# API should work again
curl http://localhost:8000/api/cases/
```

## Performance Testing

### Load Test with Multiple Cases

```bash
#!/bin/bash

for i in {1..10}; do
  curl -X POST http://localhost:8000/api/cases/ \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"Patient $i\",
      \"age\": $((30 + i)),
      \"gender\": \"M\",
      \"main_complaint\": \"Test complaint $i\"
    }" &
done

wait
```

### Query Performance

```bash
# Time a list query with 100 cases
time curl "http://localhost:8000/api/cases/?limit=100&offset=0"

# Time statistics query
time curl http://localhost:8000/api/cases/statistics/summary
```

## Cleanup

### Clear All Data (Destructive)

```bash
# WARNING: This deletes all data

docker-compose down
docker volume rm motor-biomecanico_postgres_data

# Restart to re-initialize with seed data
docker-compose up -d
```

### Logs

```bash
# Backend logs
docker-compose logs backend

# Database logs
docker-compose logs postgres

# Follow logs in real-time
docker-compose logs -f
```

## Troubleshooting

### Database Connection Refused

```
Connection refused when starting backend

Solution:
1. Check PostgreSQL is running: docker-compose ps
2. Wait longer for PostgreSQL health check (up to 10 seconds)
3. Check logs: docker-compose logs postgres
4. Verify DATABASE_URL matches container network
```

### No Data Persists

```
Data disappears after restart

Solution:
1. Check volume is mounted: docker volume ls
2. Verify docker-compose.yml has postgres_data volume
3. Ensure volume is not cleaned between restarts
4. Check: docker-compose up -d (without down)
```

### API Returns 500 Error

```
Internal Server Error on API calls

Solution:
1. Check backend logs: docker-compose logs backend
2. Verify database is healthy: docker-compose ps
3. Check for SQLAlchemy errors in logs
4. Restart backend: docker-compose restart backend
```

## Success Criteria

- [x] All 15 endpoints respond with 200/201 status codes
- [x] Database data persists across service restarts
- [x] Audit trail records all adjustments
- [x] Proper error handling with appropriate status codes
- [x] Transaction rollback on errors
- [x] Status transitions follow workflow
- [x] Pagination works correctly
- [x] Filtering by status works
- [x] Statistics aggregated correctly
- [x] Patient cases retrieved correctly

---

**Motor Biomecânico API Testing Guide v1.0**  
For questions or issues, check Phase 5 Integration Summary and Database Guide.
