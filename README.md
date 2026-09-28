# Motor Biomecânico Paramétrico

Sistema de IA para geração de palmilhas ortopédicas 3D customizadas baseado em análise biomecânica.

**Status:** MVP Development 🚧  
**Data:** Setembro 2026  
**Projeto:** Quiropraxia Pinheiros

---

## 🏗️ Arquitetura

```
motor-biomecanico/
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── core/              # Config, security, deps
│   │   ├── models/            # Pydantic models
│   │   ├── services/          # Business logic
│   │   ├── api/               # Endpoints
│   │   └── database/          # SQLAlchemy models
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── main.py
│
├── frontend/                   # React/TypeScript
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── docs/                       # Documentação
│   ├── API.md
│   ├── DEVELOPMENT.md
│   └── DEPLOYMENT.md
│
├── docker-compose.yml
├── .gitignore
└── README.md (este arquivo)
```

---

## 🚀 Quick Start

### Backend (Python FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
python main.py
```

Backend rode em `http://localhost:8000`  
Docs Swagger em `http://localhost:8000/docs`

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Frontend rode em `http://localhost:5173`

### Docker Compose (Ambos juntos)

```bash
docker-compose up --build
```

---

## 📋 Features

### MVP Phase 1 (4 semanas)

- ✅ Extração básica de parâmetros biomecânicos
- ✅ Motor de sugestões (2-3 regras clínicas)
- ✅ Geometria 3D parametrizada (CadQuery)
- ✅ Exportação STL
- ✅ Interface web de revisão
- ✅ Persistência básica (SQLite)

### Phase 2 (Refinement)

- Fotogrametria profissional
- 5-6 regras clínicas adicionais
- Simulação de pressão (heatmaps)
- Dashboard de pacientes
- Feedback clínico

### Phase 3 (Escalabilidade)

- Aprendizado contínuo (ML v2.0)
- Integração com QuiroGestão
- Automatização impressão 3D

---

## 📚 API Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/cases/analyze` | Analisar fotos de pé |
| GET | `/api/cases/{id}` | Obter caso clínico |
| POST | `/api/cases/{id}/suggestions` | Gerar sugestões |
| POST | `/api/cases/{id}/apply` | Aplicar ajustes |
| POST | `/api/cases/{id}/export-stl` | Exportar STL |
| GET | `/api/cases` | Listar casos |

---

## 🔧 Tecnologias

**Backend:**
- Python 3.11+
- FastAPI
- SQLAlchemy + SQLite
- CadQuery (geometria 3D)
- NumPy, SciPy
- Pydantic

**Frontend:**
- React 18+
- TypeScript
- Vite
- TailwindCSS
- Three.js (visualização 3D)

**Infra:**
- Docker & Docker Compose
- PostgreSQL (opcional, Phase 2)

---

## 📖 Documentação

- [API Reference](./docs/API.md)
- [Development Guide](./docs/DEVELOPMENT.md)
- [Deployment](./docs/DEPLOYMENT.md)
- [Especificação Técnica](./docs/MOTOR_BIOMECANICO.md)

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm run test
```

---

## 🤝 Contribuição

1. Fork o repo
2. Crie uma branch (`git checkout -b feature/xyz`)
3. Commit (`git commit -am 'Add feature'`)
4. Push (`git push origin feature/xyz`)
5. Abra um Pull Request

---

## 📝 Roadmap

- [ ] MVP backend funcional
- [ ] Interface web básica
- [ ] Testes unitários
- [ ] Testes clínicos (10-20 pacientes)
- [ ] Dashboard de casos
- [ ] Simulação biomecânica
- [ ] Integração QuiroGestão
- [ ] Aprendizado contínuo

---

## 📞 Contato

**Desenvolvido para:** Quiropraxia Pinheiros  
**Autor:** Claude (Anthropic)  
**Data:** Setembro 2026

---

## 📄 Licença

Proprietário - Quiropraxia Pinheiros
