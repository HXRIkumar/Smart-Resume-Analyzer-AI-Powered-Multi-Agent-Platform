"""Tests for AI agents."""

import pytest

from app.agents.parser_agent import ParserAgent
from app.agents.skill_analyzer_agent import SkillAnalyzerAgent
from app.agents.ats_evaluator_agent import ATSEvaluatorAgent


@pytest.mark.asyncio
async def test_skill_analyzer_extracts_skills():
    """Test that SkillAnalyzerAgent extracts skills from text."""
    agent = SkillAnalyzerAgent()
    context = {
        "raw_text": "I am proficient in Python, JavaScript, and React. "
        "I have experience with Docker, PostgreSQL, and AWS. "
        "Strong leadership and communication skills."
    }
    result = await agent.execute(context)
    assert "extracted_skills" in result
    assert result["skill_count"] > 0

    skill_names = [s["name"].lower() for s in result["extracted_skills"]]
    assert "python" in skill_names
    assert "javascript" in skill_names
    assert "react" in skill_names


@pytest.mark.asyncio
async def test_skill_analyzer_empty_text():
    """Test skill analyzer with empty text."""
    agent = SkillAnalyzerAgent()
    result = await agent.execute({"raw_text": ""})
    assert result["skill_count"] == 0


@pytest.mark.asyncio
async def test_skill_analyzer_missing_input():
    """Test skill analyzer raises error on missing input."""
    agent = SkillAnalyzerAgent()
    with pytest.raises(ValueError, match="missing required context keys"):
        await agent.execute({})


@pytest.mark.asyncio
async def test_ats_evaluator_scores():
    """Test ATS evaluator returns a score."""
    agent = ATSEvaluatorAgent()
    context = {
        "raw_text": """John Doe
john@example.com | 555-123-4567

EXPERIENCE
Senior Software Engineer | Google | 2020-Present
- Developed microservices architecture serving 1M+ users
- Led team of 5 engineers, improving deployment speed by 40%
- Implemented CI/CD pipeline reducing release time by 60%

EDUCATION
BS Computer Science | MIT | 2016-2020

SKILLS
Python, Java, Kubernetes, Docker, AWS, PostgreSQL"""
    }
    result = await agent.execute(context)
    assert "ats_score" in result
    assert 0 <= result["ats_score"] <= 100
    assert "ats_issues" in result


@pytest.mark.asyncio
async def test_ats_evaluator_poor_resume():
    """Test ATS evaluator flags issues in a poor resume."""
    agent = ATSEvaluatorAgent()
    context = {"raw_text": "hello world"}
    result = await agent.execute(context)
    assert result["ats_score"] < 50  # Should score low
    assert len(result["ats_issues"]) > 0


@pytest.mark.asyncio
async def test_skill_match_against_job():
    """Test skill matching against job requirements."""
    agent = SkillAnalyzerAgent()
    extracted = [
        {"name": "Python", "category": "programming", "proficiency": "advanced"},
        {"name": "React", "category": "frameworks", "proficiency": "intermediate"},
        {"name": "Docker", "category": "cloud", "proficiency": "beginner"},
    ]
    required = ["Python", "React", "Kubernetes", "Go"]
    result = agent.match_against_job(extracted, required)

    assert "matched_skills" in result
    assert "skill_gaps" in result
    assert "python" in result["matched_skills"]
    assert "kubernetes" in result["skill_gaps"]
    assert 0 <= result["skill_match_score"] <= 100
