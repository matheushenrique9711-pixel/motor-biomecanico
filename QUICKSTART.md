# Motor Biomecânico - Quick Start Guide

Get the Motor Biomecânico backend running in 5 minutes.

## Prerequisites

- Python 3.11+
- pip
- Git

## Installation & Running

### Step 1: Navigate to Backend Directory

```bash
cd motor-biomecanico/backend
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Server

```bash
python main.py
```

You should see:
```
🚀 Motor Biomecânico iniciando...
📚 Documentação disponível em: http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 5: Access the API

- **API Base**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Test the API

### 1. Create a Case

```bash
curl -X POST http://localhost:8000/api/cases/ \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "pat-001",
    "name": "João Silva",
    "age": 45,
    "gender": "M",
    "main_complaint": "Dor no arco medial ao caminhar"
  }'
```

Response will include a `case_id`. Save it for next steps.

### 2. Analyze Biomechanical Profile

```bash
curl -X POST http://localhost:8000/api/cases/case-abc123/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "foot_length": 250.0,
    "arch_length_midfoot": 120.0,
    "forefoot_width": 95.0,
    "midfoot_width": 85.0,
    "hindfoot_width": 65.0,
    "arch_height_at_50pct": 10.0,
    "arch_height_at_midfoot": 12.0,
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
  }'
```

### 3. Generate Clinical Suggestions

```bash
curl -X POST http://localhost:8000/api/cases/case-abc123/suggestions
```

This will return suggestions like:
```json
{
  "case_id": "case-abc123",
  "status": "suggestions_generated",
  "suggestions": [
    {
      "suggestion_id": "sug-12345",
      "condition_type": "flatfoot",
      "condition_name": "Pé Plano",
      "confidence": 0.85,
      "parameter_adjustments": [
        {
          "parameter_name": "arch_height_medial",
          "suggested_value": 6.0,
          "priority": 1,
          "reason": "Elevação do arco medial..."
        }
      ]
    }
  ]
}
```

### 4. Confirm Suggestions

```bash
curl -X POST http://localhost:8000/api/cases/case-abc123/confirm-suggestions \
  -H "Content-Type: application/json" \
  -d '{
    "clinician_id": "dr-001",
    "clinician_notes": "Approved as suggested"
  }'
```

### 5. Apply Insole Parameters

```bash
curl -X POST http://localhost:8000/api/cases/case-abc123/apply-adjustments \
  -H "Content-Type: application/json" \
  -d '{
    "base_thickness_mm": 4.5,
    "arch_height_medial": 6.0,
    "medial_arch_stiffness": 1.3,
    "heel_cup_depth_mm": 3.0
  }'
```

### 6. Export STL

```bash
curl -X POST http://localhost:8000/api/cases/case-abc123/export-stl \
  -H "Content-Type: application/json" \
  -d '{
    "export_format": "stl",
    "export_quality": "medium",
    "include_metadata": true
  }'
```

### 7. Get Case Details

```bash
curl http://localhost:8000/api/cases/case-abc123
```

### 8. Add Feedback

```bash
curl -X POST http://localhost:8000/api/cases/case-abc123/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "clinical_feedback": "Paciente relata melhora significativa na dor",
    "patient_feedback": "Muito confortável, uso o dia todo",
    "effectiveness_score": 8.5,
    "comfort_score": 9.0,
    "should_be_learning_case": true
  }'
```

## Interactive Testing with Swagger

The easiest way to test is using the built-in Swagger UI:

1. Open http://localhost:8000/docs
2. Click on each endpoint to expand it
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

## Run Tests

```bash
pytest tests/ -v
```

## Project Structure

```
backend/
├── app/
│   ├── models/           # Data models (biomechanical, insole, clinical, case)
│   ├── services/         # Business logic (suggestion engine, case manager)
│   ├── api/routes/       # API endpoints
│   ├── core/             # Configuration
│   └── main.py           # FastAPI app
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── tests/                # Tests
└── .env.example          # Environment config template
```

## Environment Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` to customize settings (database, CORS origins, feature flags, etc.)

## Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/cases/` | Create new case |
| GET | `/api/cases/{case_id}` | Get case details |
| GET | `/api/cases/` | List cases |
| POST | `/api/cases/{case_id}/analyze` | Register biomechanical analysis |
| POST | `/api/cases/{case_id}/suggestions` | Generate clinical suggestions |
| POST | `/api/cases/{case_id}/confirm-suggestions` | Clinician confirmation |
| POST | `/api/cases/{case_id}/apply-adjustments` | Apply insole parameters |
| POST | `/api/cases/{case_id}/export-stl` | Generate and export STL |
| POST | `/api/cases/{case_id}/feedback` | Register feedback |

## Troubleshooting

### Port 8000 Already in Use

```bash
# Change port in main.py or use:
python -m uvicorn app.main:app --port 8001
```

### Module Import Errors

Make sure you're in the virtual environment:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows
```

### Missing Dependencies

```bash
pip install -r requirements.txt --upgrade
```

## Next Steps

1. **Test the API** - Use Swagger or curl commands above
2. **Create test cases** - Submit different biomechanical profiles
3. **Review suggestions** - See how clinical rules are applied
4. **Integrate Frontend** - When React frontend is ready
5. **Add Image Processing** - For automated foot scan analysis

## Documentation

- Full API reference: http://localhost:8000/docs
- Development status: `DEVELOPMENT_STATUS.md`
- Technical specification: `../backend/../motor-biomecanico-parametrico-completo.md`

## Support

For issues or questions:
1. Check `DEVELOPMENT_STATUS.md` for architecture overview
2. Review test cases in `tests/test_models.py` for usage examples
3. Check API docs at `/docs` for endpoint contracts

---

**Ready to go!** 🚀 Your Motor Biomecânico backend is now running and ready for clinical case management.
