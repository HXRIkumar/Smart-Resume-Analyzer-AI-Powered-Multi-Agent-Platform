<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1D9E75,100:0F6E56&height=200&section=header&text=Smart%20Resume%20Analyzer&fontSize=48&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=AI-Powered%20Multi-Agent%20Resume%20Intelligence%20Platform&descAlignY=58&descSize=18&descColor=9FE1CB" width="100%"/>

<br/>

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-1D9E75?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Google Gemini](https://img.shields.io/badge/Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)

<br/>

> **Upload a resume. Get intelligence.**
> 
> A production-grade SaaS platform that analyzes resumes using a 5-agent AI pipeline — scoring, parsing, predicting, and advising in under a second.

<br/>

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Resume PDF  →  5 AI Agents  →  Score · Skills · Career       │
│                                                                 │
│   Parser → Skill Analyzer → ATS Evaluator → Career Predictor   │
│                          → Feedback Agent                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

<br/>

[**Live Demo**](#-quick-start) · [**Architecture**](#-system-architecture) · [**API Docs**](#-api-reference) · [**Contributing**](#-contributing)

</div>

---

## ✨ What It Does

<table>
<tr>
<td width="50%">

**🎯 Resume Intelligence**
- ATS compatibility score (0–100)
- Section-by-section breakdown
- Keyword density analysis
- Formatting quality check

**🧠 AI Skill Analysis**
- Detects 200+ tech skills via spaCy NLP
- Gaps vs job description
- Proficiency scoring per skill
- Recommended learning paths

</td>
<td width="50%">

**🚀 Career Prediction**
- Matches resume to 20+ career paths
- Confidence % per role
- Skill gap to target role
- Growth trajectory suggestions

**📊 Admin Intelligence**
- Platform-wide analytics
- Score distribution histograms
- Monthly upload trends
- Top missing sections across all users

</td>
</tr>
</table>

---

## 🤖 The 5-Agent Pipeline

```
                        ┌──────────────────────────────────────┐
                        │         RESUME PDF UPLOADED          │
                        └──────────────────┬───────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────────┐
                    │  🔍 AGENT 1: Parser Agent                    │
                    │  pdfplumber → raw text + section detection   │
                    │  Output: {raw_text, sections, word_count}    │
                    └──────────────────────┬───────────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────────┐
                    │  🧩 AGENT 2: Skill Analyzer Agent            │
                    │  spaCy NER + pattern matching (200+ skills)  │
                    │  Output: {present_skills, missing_skills}    │
                    └──────────┬────────────────────┬──────────────┘
                               │                    │
          ┌────────────────────▼──────┐  ┌──────────▼─────────────────┐
          │ ⚡ AGENT 3: ATS Evaluator │  │ 🎯 AGENT 4: Career Predictor│
          │ Scores 5 dimensions       │  │ scikit-learn similarity     │
          │ objectives/skills/        │  │ Top 3 career predictions    │
          │ projects/formatting/      │  │ with confidence %           │
          │ experience                │  │                             │
          └────────────────────┬──────┘  └──────────┬─────────────────┘
                               │                    │
                    ┌──────────▼────────────────────▼───────────────┐
                    │  💬 AGENT 5: Feedback Agent (Gemini AI)       │
                    │  Synthesizes all results → human feedback     │
                    │  Output: summary + 3 specific suggestions     │
                    └──────────────────────┬───────────────────────┘
                                           │
                    ┌──────────────────────▼───────────────────────┐
                    │         RESULTS SAVED TO POSTGRESQL          │
                    │   Score · Skills · Predictions · Feedback    │
                    └──────────────────────────────────────────────┘
```

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DOCKER COMPOSE                              │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌────────┐   ┌─────────┐  │
│  │   Frontend   │    │   Backend    │    │Postgres│   │  Redis  │  │
│  │  React 18    │───▶│  FastAPI     │───▶│  DB    │   │ Cache   │  │
│  │  Vite        │    │  Python 3.11 │    │ Port   │   │ Port    │  │
│  │  Port 5173   │    │  Port 8000   │    │ 5432   │   │ 6379    │  │
│  └──────────────┘    └──────┬───────┘    └────────┘   └─────────┘  │
│                             │                                       │
│                    ┌────────▼────────┐                              │
│                    │  Agent Pipeline │                              │
│                    │  5 AI Agents    │                              │
│                    │  spaCy + Gemini │                              │
│                    └─────────────────┘                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, TailwindCSS, Recharts | Dashboard, AI Lab, Analysis pages |
| **State** | Zustand, React Router v6 | Global state, routing |
| **Backend** | FastAPI, Uvicorn | REST API, async request handling |
| **ORM** | SQLAlchemy 2.0 async | Database operations |
| **Database** | PostgreSQL 15 | Persistent data storage |
| **Cache** | Redis 7 | Session caching |
| **NLP** | spaCy en_core_web_sm | Skill extraction, NER |
| **ML** | scikit-learn | Career path prediction |
| **AI** | Google Gemini 1.5 | Natural language feedback |
| **Auth** | JWT + Google OAuth 2.0 | Secure authentication |
| **PDF** | pdfplumber | Resume text extraction |
| **Infra** | Docker, Docker Compose | Containerized deployment |

---

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** — [download here](https://docker.com/products/docker-desktop) (must be running)
- **Git**

### 1. Clone

```bash
git clone https://github.com/HXRIkumar/Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform.git
cd Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in:

```env
SECRET_KEY=any-random-32-character-string-here
GEMINI_API_KEY=your-key-from-aistudio.google.com   # free tier works
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com  # optional
```

> 💡 Get Gemini API key free at [aistudio.google.com](https://aistudio.google.com) → Get API Key

### 3. Start everything

```bash
docker compose up --build
```

First run takes ~3 minutes to build. You'll see:
```
sra-backend  | INFO: Application startup complete.
sra-frontend | VITE v5.x  ready in 92 ms  →  Local: http://localhost:5173/
```

### 4. Initialize database

```bash
# In a new terminal tab:
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_data.py
```

### 5. Open the app

```
http://localhost:5173
```

| Account | Email | Password |
|---------|-------|----------|
| Admin | admin@smartresume.com | Admin123! |
| User | test@smartresume.com | Test123! |

---

## 📁 Project Structure

```
smart-resume-analyzer/
│
├── backend/                          # FastAPI application
│   ├── app/
│   │   ├── agents/                   # 🤖 The 5 AI agents
│   │   │   ├── base_agent.py         # Abstract base with timing & logging
│   │   │   ├── parser_agent.py       # PDF text extraction
│   │   │   ├── skill_analyzer_agent.py  # NLP skill detection
│   │   │   ├── ats_evaluator_agent.py   # Resume scoring
│   │   │   ├── career_prediction_agent.py # ML career matching
│   │   │   ├── feedback_agent.py     # Gemini AI feedback
│   │   │   └── pipeline.py           # Agent orchestrator
│   │   │
│   │   ├── routers/                  # API endpoints
│   │   │   ├── auth.py               # /auth/* (login, register, OAuth)
│   │   │   ├── resume.py             # /resume/* (upload, list, delete)
│   │   │   ├── analysis.py           # /analysis/* (run, result, history)
│   │   │   ├── job.py                # /job/* (job description submit)
│   │   │   └── admin.py              # /admin/* (analytics, users)
│   │   │
│   │   ├── models/                   # SQLAlchemy models
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── services/                 # Business logic layer
│   │   └── utils/                    # Security, file utils, exceptions
│   │
│   ├── alembic/                      # Database migrations
│   ├── scripts/                      # Seed data scripts
│   ├── tests/                        # pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                         # React application
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Login.jsx             # Auth page
│   │   │   ├── Dashboard.jsx         # Upload + score overview
│   │   │   ├── AILab.jsx             # Agent pipeline visualization
│   │   │   ├── Analysis.jsx          # Detailed results
│   │   │   └── AdminDashboard.jsx    # Admin analytics
│   │   │
│   │   ├── api/                      # Axios API clients
│   │   ├── store/                    # Zustand state stores
│   │   └── components/               # Reusable UI components
│   │
│   └── Dockerfile
│
├── docker-compose.yml                # Development environment
├── docker-compose.prod.yml           # Production overrides
├── .env.example                      # Environment template
└── Makefile                          # Developer shortcuts
```

---

## 🛠 Developer Commands

```bash
make dev          # Start all services (hot reload)
make migrate      # Run database migrations
make seed         # Create test users + sample data
make test         # Run pytest with coverage
make logs         # Stream backend logs
make shell        # Open bash inside backend container
make psql         # Open PostgreSQL shell
make clean        # Stop + remove all containers and volumes
```

---

## 📡 API Reference

### Authentication

```http
POST /auth/register
POST /auth/login
POST /auth/google-login
GET  /auth/me
```

### Resume

```http
POST /resume/upload          # Upload PDF (multipart/form-data)
GET  /resume/                # List user's resumes
DELETE /resume/{id}          # Delete a resume
```

### Analysis

```http
POST /analysis/run           # Trigger full AI pipeline
GET  /analysis/result/{id}   # Get analysis results
GET  /analysis/my            # List user's analyses
```

### Admin

```http
GET /admin/analytics         # Platform statistics
GET /admin/users             # All users (paginated)
```

### Health

```http
GET /health                  # Service health check
```

> Full interactive docs at `http://localhost:8000/docs` (Swagger UI)

---

## 🗄 Database Schema

```sql
users
├── id (UUID PK)
├── email (unique)
├── password_hash
├── full_name
├── role (user | admin)
├── google_id
└── created_at

resumes
├── id (UUID PK)
├── user_id (FK → users)
├── original_filename
├── file_path
├── extracted_text
└── uploaded_at

analysis_results
├── id (UUID PK)
├── resume_id (FK → resumes)
├── resume_score (0-100)
├── ats_score (0-100)
├── ai_confidence
├── present_skills (array)
├── missing_skills (array)
├── career_predictions (JSON)
├── keyword_heatmap (JSON)
├── strengths (array)
├── improvements (array)
├── ai_feedback_text
└── agent_pipeline_log (JSON)
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | JWT signing key (32+ chars) |
| `GEMINI_API_KEY` | ✅ | Google Gemini API key (free) |
| `GOOGLE_CLIENT_ID` | ⚪ | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | ⚪ | Google OAuth secret |
| `REDIS_URL` | ✅ | Redis connection string |
| `UPLOAD_DIR` | ✅ | PDF storage directory |
| `FRONTEND_URL` | ✅ | CORS allowed origin |

---

## 🧪 Running Tests

```bash
# Run full test suite
make test

# Or directly:
docker compose exec backend pytest -v --cov=app tests/
```

Test coverage includes:
- Auth endpoints (register, login, OAuth)
- Resume upload + validation
- Agent unit tests (parser, skill analyzer, ATS, career, feedback)
- Full pipeline integration tests

---

## 🚢 Production Deployment

```bash
# Build production images
docker compose -f docker-compose.prod.yml up --build -d

# Run migrations
docker compose exec backend alembic upgrade head
```

Production config includes:
- Multi-worker Uvicorn (4 workers)
- Nginx reverse proxy with gzip + security headers
- Resource limits (512MB backend, 128MB Redis)
- Health checks on all services
- No exposed database ports

---

## 🗺 Roadmap

- [x] Multi-agent AI pipeline
- [x] JWT + Google OAuth authentication
- [x] Resume scoring + ATS analysis
- [x] Career path prediction
- [x] Admin dashboard
- [ ] Job description matching (JD vs resume gap analysis)
- [ ] Resume rewrite suggestions (Gemini)
- [ ] Email notifications on analysis complete
- [ ] Multi-language resume support
- [ ] API rate limiting (slowapi)
- [ ] Kubernetes deployment manifests

---

## 🤝 Contributing

```bash
# Fork the repo, then:
git clone https://github.com/YOUR_USERNAME/Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform.git
cd Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform

# Create a feature branch
git checkout -b feat/your-feature-name

# Make changes, then:
git add .
git commit -m "feat: describe your change"
git push origin feat/your-feature-name

# Open a Pull Request on GitHub
```

---

## 👤 Author

<div align="center">

**Hari K**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/hari-dharmaraj)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/HXRIkumar)

*Built with FastAPI, React, spaCy, Google Gemini, and a lot of debugging* 🛠️

</div>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F6E56,100:1D9E75&height=100&section=footer" width="100%"/>

**⭐ Star this repo if it helped you!**

</div>
