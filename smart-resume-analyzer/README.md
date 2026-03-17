<div align="center">

# 🧠 Smart Resume Analyzer

### *AI-Powered Multi-Agent Platform for Intelligent Resume Analysis*

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=22&pause=1000&color=6C63FF&center=true&vCenter=true&random=false&width=600&lines=Upload+Your+Resume+%F0%9F%93%84;AI+Agents+Analyze+It+%F0%9F%A4%96;Get+ATS+Score+%2B+Feedback+%F0%9F%93%8A;Predict+Your+Career+Path+%F0%9F%9A%80" alt="Typing SVG" />

<br/>

> **A production-grade SaaS platform that leverages a multi-agent AI pipeline to parse, evaluate, score, and provide actionable feedback on resumes — helping job seekers land their dream roles.**

<br/>

[🚀 Quick Start](#-quick-start) •
[✨ Features](#-features) •
[🏗️ Architecture](#%EF%B8%8F-system-architecture) •
[🤖 AI Agents](#-multi-agent-ai-pipeline) •
[📋 API Docs](#-api-endpoints) •
[🛠️ Tech Stack](#%EF%B8%8F-tech-stack)

</div>

<br/>

---

<br/>

## ✨ Features

<table>
<tr>
<td width="50%">

### 📄 Smart PDF Parsing
Extracts raw text from resume PDFs with high accuracy using **pdfplumber**. Handles multi-page documents, tables, and complex layouts.

### 🎯 AI-Powered Skill Extraction
NLP-driven skill identification and categorization — detects **technical**, **soft**, and **domain-specific** skills automatically.

### 📊 ATS Compatibility Scoring
Evaluates resume compatibility with Applicant Tracking Systems using **regex-based heuristics** and structural analysis. Provides a 0–100 score.

### 🔮 Career Path Prediction
Hybrid **rule-based + LLM** approach predicts top career paths based on extracted skills, experience, and industry trends.

</td>
<td width="50%">

### 💬 GPT-Powered Feedback
Generates detailed, actionable resume improvement suggestions using **OpenAI GPT-4o-mini** — from formatting tips to content rewrites.

### 📈 Interactive Dashboard
Real-time analytics with **Recharts** — visual score breakdowns, skill gap analysis, and trend tracking in a sleek dark interface.

### 🔐 Secure Authentication
**JWT + Google OAuth 2.0** authentication with role-based access control. Passwords hashed with bcrypt.

### 🛡️ Admin Panel
Platform-wide analytics, user management, and system monitoring. Track usage stats and manage the entire platform.

</td>
</tr>
</table>

<br/>

---

<br/>

## 🏗️ System Architecture

```
                              ┌──────────────────────────────────────────────────────┐
                              │                   SMART RESUME ANALYZER              │
                              └──────────────────────┬───────────────────────────────┘
                                                     │
                    ┌────────────────────────────────┼────────────────────────────────┐
                    │                                │                                │
            ┌───────▼───────┐               ┌───────▼───────┐                ┌───────▼───────┐
            │               │               │               │                │               │
            │  🖥️ FRONTEND  │◄─── REST ───►│  ⚙️ BACKEND   │◄─── ORM ────►│  🗄️ DATABASE  │
            │  React + Vite │    API        │  FastAPI       │               │  PostgreSQL   │
            │  Tailwind CSS │               │  Async Python  │               │               │
            │  Zustand      │               │                │          ┌────►  Redis Cache  │
            │               │               │                │          │    │               │
            └───────────────┘               └───────┬────────┘          │    └───────────────┘
                                                    │                   │
                                                    │                   │
                                            ┌───────▼───────────────────┴───┐
                                            │     🤖 MULTI-AGENT PIPELINE   │
                                            │                               │
                                            │   ┌─────────────────────────┐ │
                                            │   │ 1. 📄 ParserAgent       │ │
                                            │   │ 2. 🎯 SkillAnalyzer     │ │
                                            │   │ 3. 📊 ATSEvaluator      │ │
                                            │   │ 4. 💬 FeedbackAgent     │ │
                                            │   │ 5. 🔮 CareerPredictor   │ │
                                            │   └─────────────────────────┘ │
                                            │              │                │
                                            │        ┌─────▼─────┐         │
                                            │        │  OpenAI   │         │
                                            │        │  GPT-4o   │         │
                                            │        └───────────┘         │
                                            └───────────────────────────────┘
```

<br/>

---

<br/>

## 🤖 Multi-Agent AI Pipeline

The heart of the platform — **5 specialized AI agents** work in sequence, each building on the previous agent's output to deliver comprehensive resume analysis.

```
📄 Resume PDF
     │
     ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   PARSER    │───►│  SKILL          │───►│  ATS             │───►│  FEEDBACK       │───►│  CAREER          │
│   AGENT     │    │  ANALYZER       │    │  EVALUATOR       │    │  AGENT          │    │  PREDICTOR       │
│             │    │                 │    │                  │    │                 │    │                  │
│ • PDF → Text│    │ • NLP Extract   │    │ • Score 0-100   │    │ • GPT-4o Mini   │    │ • Rule-Based     │
│ • pdfplumber│    │ • Categorize    │    │ • Regex Checks  │    │ • Suggestions   │    │ • LLM Hybrid     │
│ • Multi-page│    │ • Tech/Soft/    │    │ • Structure     │    │ • Improvements  │    │ • Top Paths      │
│             │    │   Domain        │    │   Analysis      │    │                 │    │ • Industry Trends │
└─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘    └──────────────────┘
                                                                                              │
                                                                                              ▼
                                                                                    📊 Comprehensive
                                                                                       Analysis Report
```

<br/>

| # | Agent | Purpose | Technology |
|---|-------|---------|------------|
| 1 | **🔍 ParserAgent** | Extracts raw text from uploaded PDF resumes | `pdfplumber` |
| 2 | **🎯 SkillAnalyzerAgent** | Identifies and categorizes skills (technical, soft, domain) | `NLP` + `keyword matching` |
| 3 | **📊 ATSEvaluatorAgent** | Scores ATS compatibility with detailed breakdown | `regex` + `heuristics` |
| 4 | **💬 FeedbackAgent** | Generates actionable improvement suggestions | `OpenAI GPT-4o-mini` |
| 5 | **🔮 CareerPredictionAgent** | Predicts career paths based on skill profile | `rule-based` + `LLM hybrid` |

<br/>

**Scoring Formula:**
```
Overall Score = (ATS Score × 0.4) + (Skill Match Score × 0.6)
```

<br/>

---

<br/>

## 🚀 Quick Start

### 📋 Prerequisites

| Tool | Version | Required |
|------|---------|----------|
| Python | 3.12+ | ✅ |
| Node.js | 20+ | ✅ |
| PostgreSQL | 16+ | ✅ |
| Redis | 7+ | ✅ |
| Docker & Docker Compose | Latest | 🟡 Optional |

<br/>

### 🐳 Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/HXRIkumar/Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform.git
cd Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform/smart-resume-analyzer

# Configure environment
cp .env.example .env
# ✏️ Edit .env — add your OpenAI API key and other secrets

# 🚀 Launch everything with one command
make docker-up
```

> **Access Points:**
> | Service | URL |
> |---------|-----|
> | 🖥️ Frontend | [http://localhost:5173](http://localhost:5173) |
> | ⚙️ Backend API | [http://localhost:8000](http://localhost:8000) |
> | 📚 API Docs (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) |

<br/>

### 💻 Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/HXRIkumar/Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform.git
cd Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform/smart-resume-analyzer

# 1️⃣  Configure environment
cp .env.example .env

# 2️⃣  Install all dependencies (backend + frontend)
make install

# 3️⃣  Ensure PostgreSQL & Redis are running on default ports

# 4️⃣  Run database migrations
make migrate

# 5️⃣  Start development servers
make dev
```

<br/>

---

<br/>

## 📋 API Endpoints

<details>
<summary><strong>🔐 Authentication</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register new user |
| `POST` | `/auth/login` | Login with email/password |
| `POST` | `/auth/google` | Google OAuth login |
| `GET` | `/auth/me` | Get current user profile |

</details>

<details>
<summary><strong>📄 Resume Management</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/resume/upload` | Upload resume PDF |
| `GET` | `/resume/list` | List user's resumes |
| `GET` | `/resume/{id}` | Get resume details |
| `DELETE` | `/resume/{id}` | Delete a resume |

</details>

<details>
<summary><strong>🤖 Analysis</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analysis/run/{resume_id}` | Run AI analysis pipeline |
| `GET` | `/analysis/{id}` | Get analysis results |
| `GET` | `/analysis/history` | Analysis history |

</details>

<details>
<summary><strong>💼 Job Descriptions</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/job/create` | Add job description |
| `GET` | `/job/list` | List job descriptions |

</details>

<details>
<summary><strong>🛡️ Admin</strong></summary>

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/stats` | Platform-wide statistics |
| `GET` | `/admin/users` | List all users |
| `GET` | `/health` | Health check |

</details>

<br/>

---

<br/>

## 🛠️ Tech Stack

<table>
<tr>
<td valign="top" width="33%">

### ⚙️ Backend
<br/>

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)

- **FastAPI** — Async web framework
- **SQLAlchemy 2.0** — Async ORM
- **Alembic** — Database migrations
- **Pydantic v2** — Data validation
- **pdfplumber** — PDF extraction
- **spaCy** — NLP processing
- **python-jose** — JWT tokens

</td>
<td valign="top" width="33%">

### 🖥️ Frontend
<br/>

![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Zustand](https://img.shields.io/badge/Zustand-433E38?style=flat-square&logo=react&logoColor=white)

- **React 18** — UI library
- **Vite** — Lightning-fast builds
- **Tailwind CSS 3** — Utility-first CSS
- **Zustand** — State management
- **Recharts** — Data visualization
- **React Router v6** — Routing
- **Axios** — HTTP client

</td>
<td valign="top" width="33%">

### 🏗️ Infrastructure
<br/>

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat-square&logo=nginx&logoColor=white)

- **PostgreSQL 16** — Primary database
- **Redis 7** — Caching & sessions
- **Docker Compose** — Container orchestration
- **Nginx** — Reverse proxy
- **Alembic** — Schema migrations

</td>
</tr>
</table>

<br/>

---

<br/>

## 📁 Project Structure

```
Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform/
│
├── 📦 smart-resume-analyzer/
│   │
│   ├── ⚙️ backend/
│   │   ├── app/
│   │   │   ├── 🤖 agents/              # Multi-agent AI pipeline
│   │   │   │   ├── base_agent.py        #   Base agent class
│   │   │   │   ├── parser_agent.py      #   PDF text extraction
│   │   │   │   ├── skill_analyzer_agent.py  #   Skill identification
│   │   │   │   ├── ats_evaluator_agent.py   #   ATS scoring
│   │   │   │   ├── feedback_agent.py    #   GPT feedback generation
│   │   │   │   ├── career_prediction_agent.py  #   Career prediction
│   │   │   │   └── pipeline.py          #   Pipeline orchestrator
│   │   │   │
│   │   │   ├── 🌐 routers/             # API route handlers
│   │   │   │   ├── auth.py              #   Authentication endpoints
│   │   │   │   ├── resume.py            #   Resume CRUD
│   │   │   │   ├── analysis.py          #   Analysis endpoints
│   │   │   │   ├── job.py               #   Job description matching
│   │   │   │   └── admin.py             #   Admin dashboard API
│   │   │   │
│   │   │   ├── 📊 models/              # SQLAlchemy ORM models
│   │   │   ├── 📝 schemas/             # Pydantic request/response schemas
│   │   │   ├── 🔧 services/            # Business logic layer
│   │   │   ├── 🛠️  utils/               # Helpers (security, files, exceptions)
│   │   │   │
│   │   │   ├── main.py                  # FastAPI application entry
│   │   │   ├── config.py               # Pydantic settings
│   │   │   ├── database.py             # Async SQLAlchemy engine
│   │   │   └── dependencies.py         # Auth & DB dependencies
│   │   │
│   │   ├── alembic/                     # Database migrations
│   │   ├── tests/                       # Pytest test suite
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── 🖥️ frontend/
│   │   ├── src/
│   │   │   ├── 🔌 api/                 # Axios API client layer
│   │   │   ├── 🧩 components/          # Reusable UI components
│   │   │   │   ├── Charts/             #   Recharts visualizations
│   │   │   │   ├── Layout/             #   Sidebar, Topbar
│   │   │   │   └── UI/                 #   ScoreCard, SkillChip, Feed
│   │   │   ├── 📄 pages/               # Route-level pages
│   │   │   │   ├── Dashboard.jsx        #   Main dashboard
│   │   │   │   ├── Analysis.jsx         #   Analysis results
│   │   │   │   ├── AILab.jsx            #   AI experimentation
│   │   │   │   ├── AdminDashboard.jsx   #   Admin panel
│   │   │   │   └── Login.jsx            #   Auth page
│   │   │   ├── 🏪 store/               # Zustand state stores
│   │   │   └── 🎨 styles/              # Global CSS
│   │   │
│   │   ├── package.json
│   │   ├── vite.config.js
│   │   ├── tailwind.config.js
│   │   └── Dockerfile
│   │
│   ├── 🐳 docker-compose.yml           # Development containers
│   ├── 🐳 docker-compose.prod.yml      # Production containers
│   ├── 📜 Makefile                      # Task automation
│   ├── 🔧 setup.sh                     # Setup script
│   └── 📋 .env.example                 # Environment template
```

<br/>

---

<br/>

## ⌨️ Available Commands

```bash
# 📦 Installation & Setup
make install          # Install all backend & frontend dependencies
make migrate          # Run Alembic database migrations

# 🚀 Development
make dev              # Start both dev servers concurrently

# 🐳 Docker
make docker-up        # Spin up all services via Docker Compose
make docker-down      # Stop and remove containers

# 🧪 Testing & Quality
make test             # Run pytest test suite
make lint             # Run ruff linter on backend
make format           # Format backend code with ruff

# 🧹 Maintenance
make clean            # Remove __pycache__ and temp files
```

<br/>

---

<br/>

## 🔐 Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost:5432/smart_resume_db` |
| `SECRET_KEY` | JWT signing key (min 32 chars) | `your-super-secret-key-here-min-32-chars` |
| `OPENAI_API_KEY` | OpenAI API key for AI agents | `sk-...` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `xxxx.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | `GOCSPX-...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `UPLOAD_DIR` | File upload directory | `./uploads` |
| `MAX_FILE_SIZE_MB` | Max upload size in MB | `10` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `ENVIRONMENT` | Runtime environment | `development` |

<br/>

---

<br/>

## 🧪 Running Tests

```bash
# Run full test suite
make test

# Run with coverage
pytest --cov=app backend/tests/

# Run specific test file
pytest backend/tests/test_agents.py -v
```

<br/>

---

<br/>

## 🐳 Docker Deployment

### Development
```bash
docker compose up -d             # Start all services
docker compose logs -f backend   # Stream backend logs
docker compose down              # Stop everything
```

### Production
```bash
docker compose -f docker-compose.prod.yml up -d
```

> Production config includes **Nginx** reverse proxy, optimized builds, and health checks.

<br/>

---

<br/>

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

<br/>

---

<br/>

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<br/>

---

<br/>

<div align="center">

### ⭐ Star this repo if you found it useful!

<br/>

**Built with ❤️ by [HXRIkumar](https://github.com/HXRIkumar)**

<br/>

![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Powered by OpenAI](https://img.shields.io/badge/Powered%20by-OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![Built with FastAPI](https://img.shields.io/badge/Built%20with-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Frontend React](https://img.shields.io/badge/Frontend-React-61DAFB?style=flat-square&logo=react&logoColor=black)

</div>
