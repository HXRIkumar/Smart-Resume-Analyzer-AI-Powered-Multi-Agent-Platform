"""CareerPredictionAgent — predicts career paths from skill profile.

Maps 22 career roles to required skill sets, computes overlap scores
against the candidate's present skills, and returns the top 3
predictions with confidence, match percentage, and growth path.
"""

import logging
from typing import Any

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# ─── Career → Required Skills Mapping (22 roles) ────────────────────────────

CAREER_SKILL_MAP: dict[str, list[str]] = {
    "Data Scientist": [
        "Python", "Machine Learning", "Statistics", "SQL", "pandas",
        "NumPy", "scikit-learn", "TensorFlow", "Deep Learning", "Data Analysis",
        "Jupyter", "Matplotlib", "R", "Feature Engineering",
    ],
    "ML Engineer": [
        "Python", "TensorFlow", "PyTorch", "Docker", "Kubernetes",
        "MLOps", "MLflow", "AWS", "scikit-learn", "Deep Learning",
        "CI/CD", "REST API", "Model Deployment", "Kubeflow",
    ],
    "Full Stack Developer": [
        "React", "Node.js", "PostgreSQL", "REST API", "Docker",
        "JavaScript", "TypeScript", "HTML", "CSS", "Git",
        "MongoDB", "Express", "Next.js", "Redis",
    ],
    "Backend Engineer": [
        "Python", "FastAPI", "PostgreSQL", "Redis", "Docker",
        "AWS", "REST API", "SQL", "Git", "Microservices",
        "Celery", "Linux", "CI/CD", "Kubernetes",
    ],
    "Frontend Developer": [
        "React", "TypeScript", "CSS", "JavaScript", "HTML",
        "Next.js", "Tailwind CSS", "Redux", "GraphQL", "Git",
        "Webpack", "Jest", "Figma", "Storybook",
    ],
    "Data Analyst": [
        "SQL", "Python", "Tableau", "Excel", "Statistics",
        "pandas", "Data Analysis", "Power BI", "Google Analytics",
        "Matplotlib", "Seaborn", "R", "Google Sheets",
    ],
    "DevOps Engineer": [
        "Docker", "Kubernetes", "CI/CD", "AWS", "Linux",
        "Terraform", "Ansible", "Jenkins", "Git", "Prometheus",
        "Grafana", "Helm", "Nginx", "Shell",
    ],
    "Cloud Architect": [
        "AWS", "GCP", "Azure", "Terraform", "Kubernetes",
        "Docker", "Microservices", "System Design", "Linux",
        "Networking", "Security", "IAM", "Lambda", "CloudFront",
    ],
    "AI Research Engineer": [
        "Python", "PyTorch", "Deep Learning", "Machine Learning",
        "NLP", "Computer Vision", "TensorFlow", "Transformers",
        "BERT", "Hugging Face", "NumPy", "Statistics", "LaTeX",
    ],
    "Mobile Developer": [
        "React Native", "JavaScript", "TypeScript", "Flutter",
        "iOS", "Android", "Swift", "Kotlin", "REST API",
        "Git", "Firebase", "Expo", "Redux",
    ],
    "Data Engineer": [
        "Python", "SQL", "Apache Spark", "Apache Kafka", "Airflow",
        "AWS", "Docker", "ETL", "PostgreSQL", "Data Warehousing",
        "Snowflake", "Redshift", "dbt", "Delta Lake",
    ],
    "Cybersecurity Analyst": [
        "Cybersecurity", "Linux", "Networking", "OWASP",
        "Penetration Testing", "Encryption", "SSL/TLS", "SOC 2",
        "Python", "Shell", "GDPR", "Security Auditing",
    ],
    "Site Reliability Engineer": [
        "Kubernetes", "Docker", "Linux", "Prometheus", "Grafana",
        "Terraform", "AWS", "CI/CD", "Python", "Shell",
        "Nginx", "Helm", "Datadog", "ELK Stack",
    ],
    "Product Manager (Technical)": [
        "Agile", "Scrum", "Jira", "SQL", "Data Analysis",
        "System Design", "API Design", "Figma", "Confluence",
        "A/B Testing", "Analytics", "Stakeholder Management",
    ],
    "Blockchain Developer": [
        "Solidity", "Ethereum", "Web3", "JavaScript", "React",
        "Node.js", "Rust", "Go", "Docker", "Git",
        "REST API", "PostgreSQL", "Cryptography",
    ],
    "QA / Test Engineer": [
        "Selenium", "Cypress", "Jest", "pytest", "Python",
        "JavaScript", "CI/CD", "Git", "TDD", "BDD",
        "Playwright", "JUnit", "Integration Testing", "Jira",
    ],
    "Game Developer": [
        "Unity", "C#", "C++", "Unreal Engine", "Python",
        "Git", "3D Modeling", "Physics Simulation",
        "Godot", "OpenGL", "Mathematics",
    ],
    "NLP Engineer": [
        "Python", "NLP", "Transformers", "Hugging Face", "BERT",
        "PyTorch", "TensorFlow", "scikit-learn", "Deep Learning",
        "LangChain", "OpenAI", "LLM", "spaCy",
    ],
    "Platform Engineer": [
        "Kubernetes", "Docker", "Terraform", "AWS", "Linux",
        "CI/CD", "Helm", "ArgoCD", "Prometheus", "Go",
        "Python", "Microservices", "Consul", "Vault",
    ],
    "Solutions Architect": [
        "AWS", "Azure", "System Design", "Microservices",
        "Kubernetes", "Docker", "REST API", "SQL", "NoSQL",
        "Security", "Networking", "Terraform", "API Design",
    ],
    "IoT Engineer": [
        "Python", "C++", "Raspberry Pi", "Arduino", "IoT",
        "MQTT", "AWS", "Linux", "Docker", "Networking",
        "Embedded Systems", "Sensors", "Edge Computing",
    ],
    "Computer Vision Engineer": [
        "Python", "Computer Vision", "OpenCV", "PyTorch",
        "TensorFlow", "Deep Learning", "CNN", "ONNX",
        "NumPy", "Docker", "AWS", "Model Deployment",
    ],
}


class CareerPredictionAgent(BaseAgent):
    """Predicts top career paths based on skill overlap analysis.

    Computes a match score between the candidate's skill set and
    22 predefined career role profiles. Returns the top 3 matches
    with confidence, missing skills, and growth path guidance.
    """

    name: str = "career_prediction_agent"
    version: str = "1.0.0"

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Predict career paths from the candidate's present skills.

        Args:
            input_data: Must contain:
                - present_skills (list[str]): Skills found in the resume.
                - experience_text (str): Experience section text.

        Returns:
            Dict with predictions (top 3), all_career_scores, and career_growth_path.
        """
        present_skills: list[str] = input_data.get("present_skills", [])
        experience_text: str = input_data.get("experience_text", "")

        logger.info(
            "CareerPredictionAgent — analyzing %d skills for career prediction",
            len(present_skills),
        )

        present_set = {s.lower() for s in present_skills}

        # ── Score each career path ───────────────────────────────────────
        career_scores: list[dict[str, Any]] = []

        for role, required_skills in CAREER_SKILL_MAP.items():
            required_lower = {s.lower() for s in required_skills}
            matching = present_set & required_lower
            missing = required_lower - present_set

            match_pct = (len(matching) / max(len(required_lower), 1)) * 100
            confidence = self._compute_confidence(
                match_pct, len(matching), experience_text, role
            )

            career_scores.append({
                "role": role,
                "confidence": round(confidence, 2),
                "match_percentage": round(match_pct, 1),
                "matching_skills": sorted(
                    s for s in required_skills if s.lower() in matching
                ),
                "missing_for_role": sorted(
                    s for s in required_skills if s.lower() in missing
                ),
            })

        # Sort by confidence (desc), then match_percentage (desc)
        career_scores.sort(key=lambda x: (-x["confidence"], -x["match_percentage"]))

        # ── Top 3 predictions ────────────────────────────────────────────
        top_3 = career_scores[:3]

        # ── Career growth path ───────────────────────────────────────────
        growth_path = self._compute_growth_path(top_3, present_skills)

        # ── All scores (for heatmap / UI) ────────────────────────────────
        all_scores = {
            entry["role"]: entry["match_percentage"]
            for entry in career_scores
        }

        logger.info(
            "CareerPredictionAgent — top prediction: %s (%.1f%% match)",
            top_3[0]["role"] if top_3 else "None",
            top_3[0]["match_percentage"] if top_3 else 0,
        )

        return {
            "predictions": top_3,
            "all_career_scores": all_scores,
            "career_growth_path": growth_path,
        }

    @staticmethod
    def _compute_confidence(
        match_pct: float,
        matching_count: int,
        experience_text: str,
        role: str,
    ) -> float:
        """Compute confidence score for a career prediction.

        Factors:
        - Skill overlap (70% weight)
        - Experience text relevance (20% weight)
        - Minimum skill threshold bonus (10% weight)

        Args:
            match_pct: Percentage of required skills matched.
            matching_count: Number of matching skills.
            experience_text: Experience section text.
            role: Career role name.

        Returns:
            Confidence score (0.0–1.0).
        """
        # Base: skill overlap
        skill_score = (match_pct / 100) * 0.70

        # Experience relevance: check if role keywords appear in experience
        role_words = role.lower().split()
        exp_lower = experience_text.lower()
        role_mention_count = sum(1 for w in role_words if w in exp_lower)
        exp_score = min(role_mention_count / max(len(role_words), 1), 1.0) * 0.20

        # Threshold bonus: having >= 5 matching skills shows depth
        threshold_score = min(matching_count / 5, 1.0) * 0.10

        return min(skill_score + exp_score + threshold_score, 1.0)

    @staticmethod
    def _compute_growth_path(
        top_predictions: list[dict[str, Any]],
        present_skills: list[str],
    ) -> dict[str, Any]:
        """Generate career growth path guidance.

        Args:
            top_predictions: Top 3 career predictions.
            present_skills: Current skill set.

        Returns:
            Dict with current_level, primary_path, next_steps.
        """
        skill_count = len(present_skills)

        # Determine experience level from skill count
        if skill_count >= 20:
            current_level = "Senior"
        elif skill_count >= 12:
            current_level = "Mid-Level"
        elif skill_count >= 5:
            current_level = "Junior"
        else:
            current_level = "Entry-Level"

        # Primary path from top prediction
        primary = top_predictions[0] if top_predictions else None
        primary_path = primary["role"] if primary else "General Software Engineer"

        # Next steps: focus on top missing skills from the primary career
        next_steps: list[str] = []
        if primary and primary.get("missing_for_role"):
            top_missing = primary["missing_for_role"][:5]
            next_steps.append(
                f"Learn these skills to strengthen your {primary_path} profile: "
                + ", ".join(top_missing)
            )

        if current_level in ("Entry-Level", "Junior"):
            next_steps.append("Build 2–3 portfolio projects to demonstrate hands-on experience")
            next_steps.append("Contribute to open source projects to gain real-world coding exposure")

        if current_level == "Mid-Level":
            next_steps.append("Lead a project end-to-end to demonstrate ownership and architecture skills")
            next_steps.append("Consider relevant certifications (AWS, GCP, or domain-specific)")

        if current_level == "Senior":
            next_steps.append("Mentor junior engineers and document architectural decisions")
            next_steps.append("Explore specialization or management tracks based on interest")

        return {
            "current_level": current_level,
            "primary_path": primary_path,
            "next_steps": next_steps,
        }
