"""Career prediction agent — ML-based career path prediction."""

from typing import Any

from openai import AsyncOpenAI

from app.agents.base_agent import BaseAgent
from app.config import settings


class CareerPredictionAgent(BaseAgent):
    """Predicts potential career paths based on resume skills and experience."""

    name = "career_prediction_agent"

    # Role archetypes mapped to skill clusters
    ROLE_ARCHETYPES = {
        "Backend Engineer": ["python", "java", "sql", "django", "flask", "fastapi", "postgresql", "redis"],
        "Frontend Engineer": ["javascript", "react", "angular", "vue", "typescript", "css", "html"],
        "Full-Stack Developer": ["javascript", "python", "react", "node.js", "sql", "docker"],
        "Data Scientist": ["python", "pandas", "numpy", "scikit-learn", "pytorch", "tensorflow", "r"],
        "ML Engineer": ["python", "pytorch", "tensorflow", "docker", "kubernetes", "mlops"],
        "DevOps Engineer": ["docker", "kubernetes", "terraform", "aws", "ci/cd", "jenkins", "linux"],
        "Cloud Architect": ["aws", "azure", "gcp", "terraform", "kubernetes", "networking"],
        "Data Engineer": ["python", "spark", "airflow", "kafka", "sql", "snowflake", "dbt"],
        "Product Manager": ["agile", "scrum", "leadership", "communication", "project management"],
        "Engineering Manager": ["leadership", "agile", "mentoring", "project management", "communication"],
    }

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Predict career paths based on extracted skills.

        Args:
            context: Must contain 'extracted_skills' and 'raw_text'.

        Returns:
            Dict with 'career_predictions' list.
        """
        self.validate_input(context, ["extracted_skills", "raw_text"])
        extracted = context["extracted_skills"]
        raw_text = context["raw_text"]

        # Rule-based matching
        skill_names = {s["name"].lower() for s in extracted}
        role_scores: list[dict[str, Any]] = []

        for role, required in self.ROLE_ARCHETYPES.items():
            matched = sum(1 for s in required if s in skill_names)
            confidence = round(matched / len(required), 2) if required else 0
            if confidence >= 0.2:  # At least 20% match
                role_scores.append({
                    "role": role,
                    "confidence": confidence,
                    "reasoning": f"Matched {matched}/{len(required)} core skills",
                })

        role_scores.sort(key=lambda x: x["confidence"], reverse=True)

        # Enhance with LLM if available
        try:
            llm_predictions = await self._llm_predict(raw_text[:3000], extracted)
            # Merge: prefer LLM reasoning but keep rule-based confidence
            for pred in llm_predictions:
                existing = next((r for r in role_scores if r["role"].lower() == pred["role"].lower()), None)
                if existing:
                    existing["reasoning"] = pred.get("reasoning", existing["reasoning"])
                else:
                    role_scores.append(pred)
        except Exception:
            pass  # Fall back to rule-based only

        return {"career_predictions": role_scores[:5]}

    async def _llm_predict(self, resume_text: str, skills: list[dict]) -> list[dict]:
        """Use LLM for enhanced career prediction."""
        skill_list = ", ".join(s["name"] for s in skills)
        prompt = f"""Based on this resume excerpt and skills, suggest top 3 career paths.
Resume: {resume_text}
Skills: {skill_list}

Respond as JSON array: [{{"role": "...", "confidence": 0.0-1.0, "reasoning": "..."}}]"""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.5,
        )
        import json
        content = response.choices[0].message.content or "[]"
        # Extract JSON from response
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
        return []
