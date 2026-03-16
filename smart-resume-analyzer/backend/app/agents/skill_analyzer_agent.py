"""Skill analyzer agent — NLP skill extraction using spaCy."""

from typing import Any

from app.agents.base_agent import BaseAgent


class SkillAnalyzerAgent(BaseAgent):
    """Extracts skills from resume text using NLP techniques."""

    name = "skill_analyzer_agent"

    # Common skill categories for classification
    SKILL_CATEGORIES = {
        "programming": [
            "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
            "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql",
        ],
        "frameworks": [
            "react", "angular", "vue", "django", "flask", "fastapi", "spring",
            "express", "next.js", "node.js", "rails", "laravel", ".net",
        ],
        "cloud": [
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "ci/cd", "jenkins", "github actions", "cloudformation",
        ],
        "data": [
            "pandas", "numpy", "pytorch", "tensorflow", "scikit-learn",
            "spark", "hadoop", "kafka", "airflow", "dbt", "snowflake",
        ],
        "databases": [
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "dynamodb", "cassandra", "neo4j", "sqlite",
        ],
        "soft_skills": [
            "leadership", "communication", "teamwork", "problem-solving",
            "project management", "agile", "scrum", "mentoring",
        ],
    }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Extract skills from resume text.

        Args:
            context: Must contain 'raw_text' key.

        Returns:
            Dict with 'extracted_skills' list of {name, category, proficiency}.
        """
        self.validate_input(context, ["raw_text"])
        raw_text = context["raw_text"].lower()

        extracted_skills = []
        for category, skills in self.SKILL_CATEGORIES.items():
            for skill in skills:
                if skill in raw_text:
                    # Estimate proficiency based on mention frequency
                    count = raw_text.count(skill)
                    proficiency = "advanced" if count >= 3 else "intermediate" if count >= 2 else "beginner"
                    extracted_skills.append({
                        "name": skill.title(),
                        "category": category,
                        "proficiency": proficiency,
                    })

        return {
            "extracted_skills": extracted_skills,
            "skill_count": len(extracted_skills),
        }

    def match_against_job(
        self, extracted_skills: list[dict], required_skills: list[str]
    ) -> dict[str, Any]:
        """Match extracted skills against job requirements."""
        extracted_names = {s["name"].lower() for s in extracted_skills}
        required_lower = [s.lower() for s in required_skills]

        matched = [s for s in required_lower if s in extracted_names]
        gaps = [s for s in required_lower if s not in extracted_names]

        score = (len(matched) / len(required_lower) * 100) if required_lower else 0

        return {
            "matched_skills": matched,
            "skill_gaps": gaps,
            "skill_match_score": round(score, 1),
        }
