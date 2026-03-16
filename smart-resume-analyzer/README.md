# 🧠 Smart Resume Analyzer

A production-grade SaaS platform that analyzes resumes using a **multi-agent AI pipeline**. Built with FastAPI, React, and OpenAI.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **PDF Parsing** | Extract text from resume PDFs using pdfplumber |
| **Skill Extraction** | NLP-powered skill identification and categorization |
| **ATS Scoring** | Evaluate resume compatibility with Applicant Tracking Systems |
| **AI Feedback** | GPT-powered detailed resume feedback and suggestions |
| **Career Prediction** | ML + LLM hybrid career path predictions |
| **Dashboard** | Real-time analytics with interactive charts |
| **Admin Panel** | Platform-wide stats and user management |
| **Auth** | JWT + Google OAuth authentication |

---

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────┐
│   React UI  │────▶│              FastAPI Backend              │
│  (Vite +    │     │                                          │
│   Tailwind) │     │  ┌─────────┐  ┌────────────────────────┐│
│             │◀────│  │ Routers │──│    Service Layer        ││
└─────────────┘     │  └─────────┘  │                        ││
                    │               │  ┌──────────────────┐  ││
                    │               │  │  Agent Pipeline   │  ││
                    │               │  │  ┌──────────────┐ │  ││
                    │               │  │  │ ParserAgent   │ │  ││
                    │               │  │  │ SkillAgent    │ │  ││
                    │               │  │  │ ATSAgent      │ │  ││
                    │               │  │  │ FeedbackAgent │ │  ││
                    │               │  │  │ CareerAgent   │ │  ││
                    │               │  │  └──────────────┘ │  ││
                    │               │  └──────────────────┘  ││
                    │               └────────────────────────┘│
                    │  ┌──────────┐  ┌────────┐              │
                    │  │PostgreSQL│  │ Redis  │              │
                    │  └──────────┘  └────────┘              │
                    └──────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)

### Option 1: Docker (Recommended)

```bash
# Clone and enter project
cd smart-resume-analyzer

# Copy environment file
cp .env.example .env
# Edit .env with your OpenAI API key, etc.

# Start everything
make docker-up

# Access:
# Frontend → http://localhost:5173
# Backend  → http://localhost:8000
# API Docs → http://localhost:8000/docs
```

### Option 2: Local Development

```bash
cd smart-resume-analyzer

# 1. Copy and configure environment
cp .env.example .env

# 2. Install dependencies
make install

# 3. Start PostgreSQL & Redis
#    (ensure they're running on default ports)

# 4. Run database migrations
make migrate

# 5. Start dev servers
make dev

# Frontend → http://localhost:5173
# Backend  → http://localhost:8000/docs
```

---

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `make install` | Install all backend & frontend dependencies |
| `make dev` | Start both dev servers concurrently |
| `make migrate` | Run Alembic database migrations |
| `make test` | Run pytest test suite |
| `make docker-up` | Start all services via Docker Compose |
| `make docker-down` | Stop Docker containers |
| `make lint` | Run ruff linter on backend code |
| `make format` | Format backend code with ruff |
| `make clean` | Remove __pycache__ and temp files |

---

## 🤖 AI Agent Pipeline

The analysis pipeline runs 5 agents sequentially, each building on the previous agent's output:

1. **ParserAgent** — Extracts text from PDF using pdfplumber
2. **SkillAnalyzerAgent** — Identifies and categorizes skills via keyword matching + NLP
3. **ATSEvaluatorAgent** — Scores ATS compatibility using regex-based checks
4. **FeedbackAgent** — Generates detailed feedback via OpenAI GPT-4o-mini
5. **CareerPredictionAgent** — Predicts career paths using rule-based + LLM hybrid approach

---

## 🗄️ Tech Stack

### Backend
- **FastAPI** — Async Python web framework
- **SQLAlchemy 2.0** — Async ORM with PostgreSQL
- **Alembic** — Database migrations
- **Pydantic v2** — Data validation
- **python-jose** — JWT authentication
- **pdfplumber** — PDF text extraction
- **OpenAI** — LLM integration
- **spaCy** — NLP processing

### Frontend
- **React 18** — UI library
- **Vite** — Build tool
- **Tailwind CSS 3** — Utility-first styling
- **Zustand** — Lightweight state management
- **Recharts** — Data visualization
- **React Router v6** — Client-side routing
- **Axios** — HTTP client

### Infrastructure
- **PostgreSQL 16** — Primary database
- **Redis 7** — Caching and sessions
- **Docker** — Containerization
- **Nginx** — Production static file serving

---

## 📁 Project Structure

```
smart-resume-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # Async SQLAlchemy
│   │   ├── dependencies.py      # Auth dependencies
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   ├── agents/              # AI agent pipeline
│   │   └── utils/               # Helpers
│   ├── alembic/                 # Migrations
│   ├── tests/                   # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API layer
│   │   ├── components/          # React components
│   │   ├── pages/               # Route pages
│   │   ├── store/               # Zustand stores
│   │   └── styles/              # Global CSS
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
└── .env.example
```

---

## 🔐 Environment Variables

See `.env.example` for all required variables. Key ones:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (min 32 chars) |
| `OPENAI_API_KEY` | OpenAI API key for AI agents |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `REDIS_URL` | Redis connection string |

---

## 📄 License

MIT
