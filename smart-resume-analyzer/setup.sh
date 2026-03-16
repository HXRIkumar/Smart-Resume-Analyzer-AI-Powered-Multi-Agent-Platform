#!/bin/bash
set -e

echo "🚀 Setting up Smart Resume Analyzer project scaffold..."

PROJECT_ROOT="smart-resume-analyzer"

# ─────────────────────────── Backend ───────────────────────────
mkdir -p "$PROJECT_ROOT/backend/app/models"
mkdir -p "$PROJECT_ROOT/backend/app/schemas"
mkdir -p "$PROJECT_ROOT/backend/app/routers"
mkdir -p "$PROJECT_ROOT/backend/app/services"
mkdir -p "$PROJECT_ROOT/backend/app/agents"
mkdir -p "$PROJECT_ROOT/backend/app/utils"
mkdir -p "$PROJECT_ROOT/backend/alembic/versions"
mkdir -p "$PROJECT_ROOT/backend/tests"

# Backend __init__.py files
touch "$PROJECT_ROOT/backend/app/__init__.py"
touch "$PROJECT_ROOT/backend/app/models/__init__.py"
touch "$PROJECT_ROOT/backend/app/schemas/__init__.py"
touch "$PROJECT_ROOT/backend/app/routers/__init__.py"
touch "$PROJECT_ROOT/backend/app/services/__init__.py"
touch "$PROJECT_ROOT/backend/app/agents/__init__.py"
touch "$PROJECT_ROOT/backend/app/utils/__init__.py"
touch "$PROJECT_ROOT/backend/tests/__init__.py"

# Backend core files
touch "$PROJECT_ROOT/backend/app/main.py"
touch "$PROJECT_ROOT/backend/app/config.py"
touch "$PROJECT_ROOT/backend/app/database.py"
touch "$PROJECT_ROOT/backend/app/dependencies.py"

# Models
touch "$PROJECT_ROOT/backend/app/models/user.py"
touch "$PROJECT_ROOT/backend/app/models/resume.py"
touch "$PROJECT_ROOT/backend/app/models/job_description.py"
touch "$PROJECT_ROOT/backend/app/models/analysis.py"

# Schemas
touch "$PROJECT_ROOT/backend/app/schemas/user.py"
touch "$PROJECT_ROOT/backend/app/schemas/resume.py"
touch "$PROJECT_ROOT/backend/app/schemas/analysis.py"
touch "$PROJECT_ROOT/backend/app/schemas/auth.py"

# Routers
touch "$PROJECT_ROOT/backend/app/routers/auth.py"
touch "$PROJECT_ROOT/backend/app/routers/resume.py"
touch "$PROJECT_ROOT/backend/app/routers/analysis.py"
touch "$PROJECT_ROOT/backend/app/routers/admin.py"
touch "$PROJECT_ROOT/backend/app/routers/job.py"

# Services
touch "$PROJECT_ROOT/backend/app/services/auth_service.py"
touch "$PROJECT_ROOT/backend/app/services/resume_service.py"
touch "$PROJECT_ROOT/backend/app/services/analysis_service.py"
touch "$PROJECT_ROOT/backend/app/services/admin_service.py"

# Agents
touch "$PROJECT_ROOT/backend/app/agents/base_agent.py"
touch "$PROJECT_ROOT/backend/app/agents/parser_agent.py"
touch "$PROJECT_ROOT/backend/app/agents/skill_analyzer_agent.py"
touch "$PROJECT_ROOT/backend/app/agents/ats_evaluator_agent.py"
touch "$PROJECT_ROOT/backend/app/agents/feedback_agent.py"
touch "$PROJECT_ROOT/backend/app/agents/career_prediction_agent.py"
touch "$PROJECT_ROOT/backend/app/agents/pipeline.py"

# Utils
touch "$PROJECT_ROOT/backend/app/utils/security.py"
touch "$PROJECT_ROOT/backend/app/utils/file_utils.py"
touch "$PROJECT_ROOT/backend/app/utils/exceptions.py"

# Alembic
touch "$PROJECT_ROOT/backend/alembic/env.py"
touch "$PROJECT_ROOT/backend/alembic.ini"

# Tests
touch "$PROJECT_ROOT/backend/tests/test_auth.py"
touch "$PROJECT_ROOT/backend/tests/test_resume.py"
touch "$PROJECT_ROOT/backend/tests/test_agents.py"

# Backend misc
touch "$PROJECT_ROOT/backend/requirements.txt"
touch "$PROJECT_ROOT/backend/Dockerfile"

# ─────────────────────────── Frontend ───────────────────────────
mkdir -p "$PROJECT_ROOT/frontend/public"
mkdir -p "$PROJECT_ROOT/frontend/src/api"
mkdir -p "$PROJECT_ROOT/frontend/src/components/Layout"
mkdir -p "$PROJECT_ROOT/frontend/src/components/Charts"
mkdir -p "$PROJECT_ROOT/frontend/src/components/UI"
mkdir -p "$PROJECT_ROOT/frontend/src/pages"
mkdir -p "$PROJECT_ROOT/frontend/src/store"
mkdir -p "$PROJECT_ROOT/frontend/src/styles"

# Frontend files
touch "$PROJECT_ROOT/frontend/src/main.jsx"
touch "$PROJECT_ROOT/frontend/src/App.jsx"
touch "$PROJECT_ROOT/frontend/src/api/client.js"
touch "$PROJECT_ROOT/frontend/src/api/auth.js"
touch "$PROJECT_ROOT/frontend/src/api/resume.js"
touch "$PROJECT_ROOT/frontend/src/api/analysis.js"
touch "$PROJECT_ROOT/frontend/src/components/Layout/Sidebar.jsx"
touch "$PROJECT_ROOT/frontend/src/components/Layout/Topbar.jsx"
touch "$PROJECT_ROOT/frontend/src/components/Charts/SkillsGapChart.jsx"
touch "$PROJECT_ROOT/frontend/src/components/Charts/ScoreBreakdownChart.jsx"
touch "$PROJECT_ROOT/frontend/src/components/Charts/AdminCharts.jsx"
touch "$PROJECT_ROOT/frontend/src/components/UI/ScoreCard.jsx"
touch "$PROJECT_ROOT/frontend/src/components/UI/SkillChip.jsx"
touch "$PROJECT_ROOT/frontend/src/components/UI/ActivityFeed.jsx"
touch "$PROJECT_ROOT/frontend/src/pages/Login.jsx"
touch "$PROJECT_ROOT/frontend/src/pages/Dashboard.jsx"
touch "$PROJECT_ROOT/frontend/src/pages/AILab.jsx"
touch "$PROJECT_ROOT/frontend/src/pages/Analysis.jsx"
touch "$PROJECT_ROOT/frontend/src/pages/AdminDashboard.jsx"
touch "$PROJECT_ROOT/frontend/src/store/authStore.js"
touch "$PROJECT_ROOT/frontend/src/store/analysisStore.js"
touch "$PROJECT_ROOT/frontend/src/styles/globals.css"
touch "$PROJECT_ROOT/frontend/package.json"
touch "$PROJECT_ROOT/frontend/tailwind.config.js"
touch "$PROJECT_ROOT/frontend/vite.config.js"
touch "$PROJECT_ROOT/frontend/Dockerfile"

# ─────────────────────────── Root ───────────────────────────
touch "$PROJECT_ROOT/docker-compose.yml"
touch "$PROJECT_ROOT/docker-compose.prod.yml"
touch "$PROJECT_ROOT/.env.example"
touch "$PROJECT_ROOT/.gitignore"
touch "$PROJECT_ROOT/README.md"
touch "$PROJECT_ROOT/Makefile"

echo ""
echo "✅ Project scaffold created successfully!"
echo ""
echo "📁 Structure:"
find "$PROJECT_ROOT" -type f | sort | head -80
echo ""
echo "Next steps:"
echo "  1. cd $PROJECT_ROOT"
echo "  2. cp .env.example .env"
echo "  3. make install"
echo "  4. make dev"
