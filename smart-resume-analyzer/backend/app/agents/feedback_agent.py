"""Feedback agent — LLM-powered resume feedback generation."""

from typing import Any

from openai import AsyncOpenAI

from app.agents.base_agent import BaseAgent
from app.config import settings


class FeedbackAgent(BaseAgent):
    """Generates detailed, actionable resume feedback using OpenAI GPT."""

    name = "feedback_agent"

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Generate LLM-powered feedback for a resume.

        Args:
            context: Must contain 'raw_text'. Optionally 'job_description',
                     'extracted_skills', 'ats_score'.

        Returns:
            Dict with 'feedback' string.
        """
        self.validate_input(context, ["raw_text"])

        raw_text = context["raw_text"]
        job_description = context.get("job_description", "Not provided")
        extracted_skills = context.get("extracted_skills", [])
        ats_score = context.get("ats_score", "N/A")

        skill_list = ", ".join(s["name"] for s in extracted_skills) if extracted_skills else "None extracted"

        prompt = f"""You are an expert career coach and resume reviewer. Analyze the following resume and provide detailed, actionable feedback.

## Resume Text:
{raw_text[:4000]}

## Job Description (if provided):
{job_description[:2000]}

## Extracted Skills:
{skill_list}

## ATS Score:
{ats_score}

Provide feedback in the following format:
1. **Overall Impression** — 2-3 sentences
2. **Strengths** — Top 3 strengths
3. **Areas for Improvement** — Top 3 improvements with specific suggestions
4. **Formatting Recommendations** — Any layout/structure suggestions
5. **Keyword Optimization** — Missing keywords for the target role

Be specific, professional, and encouraging."""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1500,
                temperature=0.7,
            )
            feedback = response.choices[0].message.content or "Unable to generate feedback."
        except Exception as e:
            feedback = f"Feedback generation unavailable: {str(e)}"

        return {"feedback": feedback}
