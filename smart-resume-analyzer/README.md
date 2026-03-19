# Smart Resume Analyzer

AI-powered resume analysis platform with a multi-agent pipeline that parses, scores, and provides actionable feedback on resumes.

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TailwindCSS, Recharts, Zustand, React Router v6 |
| **Backend** | FastAPI, SQLAlchemy (async), PostgreSQL, Redis |
| **AI** | spaCy NLP, scikit-learn, Google Gemini API |
| **Infrastructure** | Docker, Docker Compose, Nginx, GitHub Actions CI |

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running)
- Git

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/HXRIkumar/Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform.git
cd Smart-Resume-Analyzer-AI-Powered-Multi-Agent-Platform

# 2. Create environment file
cp .env.example .env
# Edit .env and add your keys:
#   SECRET_KEY     — any random 32+ character string
#   GEMINI_API_KEY — from aistudio.google.com (free)
#   GOOGLE_CLIENT_ID — from console.cloud.google.com (optional)

# 3. Start the application
docker compose up --build

# 4. Run database migrations (in another terminal)
docker compose exec backend alembic upgrade head

# 5. Seed test data
docker compose exec backend python scripts/seed_data.py

# 6. Open the app
open http://localhost:5173
```

**Login credentials (from seed):**

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@smartresume.com` | `Admin123!` |
| User | `alice@example.com` | `TestUser1!` |

## Features

- **Resume PDF upload** — drag-and-drop with automatic analysis
- **5-agent AI pipeline** — Parser → Skills → ATS → Career → Feedback
- **Resume score** — overall score, ATS compatibility, component breakdown
- **Skill gap analysis** — present vs. missing skills with recommendations
- **Career path predictions** — ML-based role matching with confidence scores
- **AI feedback** — Google Gemini-powered actionable suggestions
- **Admin dashboard** — platform-wide analytics, user management, score distributions

## Agent Pipeline

```
PDF Upload
    ↓
┌─────────────────┐
│  Parser Agent    │ → Extracts text from PDF (pdfplumber)
└────────┬────────┘
         ↓
┌─────────────────┐
│  Skill Analyzer  │ → Identifies 200+ tech skills via NLP
└────────┬────────┘
         ↓
┌─────────────────┐
│  ATS Evaluator   │ → Scores resume quality 0-100
└────────┬────────┘
         ↓
┌─────────────────┐
│  Career Predict  │ → Predicts best-fit roles (scikit-learn)
└────────┬────────┘
         ↓
┌─────────────────┐
│  Feedback Agent  │ → Generates suggestions (Google Gemini)
└─────────────────┘
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Login (returns JWT) |
| `POST` | `/resume/upload` | Upload PDF resume |
| `POST` | `/analysis/run` | Run AI pipeline |
| `GET` | `/analysis/result/{id}` | Get analysis results |
| `GET` | `/analysis/my` | List user's analyses |
| `GET` | `/admin/analytics` | Admin platform stats |
| `GET` | `/admin/users` | Admin user list |
| `GET` | `/health` | Health check |

## Project Structure

```
smart-resume-analyzer/
├── backend/
│   ├── app/
│   │   ├── agents/          # 5-agent AI pipeline
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── routers/         # FastAPI route handlers
│   │   ├── schemas/         # Pydantic request/response
│   │   ├── services/        # Business logic layer
│   │   └── main.py          # FastAPI app entry point
│   ├── scripts/seed_data.py # Database seeder
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios API client
│   │   ├── components/      # Charts, Layout
│   │   ├── pages/           # Dashboard, AILab, Analysis, Admin
│   │   ├── store/           # Zustand state management
│   │   └── App.jsx
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml       # Development
├── docker-compose.prod.yml  # Production
├── Makefile                 # CLI shortcuts
└── .github/workflows/ci.yml # CI pipeline
```

## Make Commands

```bash
make dev        # Start dev environment
make prod       # Start production deployment
make migrate    # Run database migrations
make seed       # Seed test data
make test       # Run backend tests
make logs       # Follow backend logs
make shell      # Open backend container shell
make clean      # Stop and remove volumes
make help       # Show all commands
```

## License

MIT
