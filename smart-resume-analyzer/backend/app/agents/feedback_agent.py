"""FeedbackAgent — generates actionable resume feedback via GPT-4o-mini.

Calls the OpenAI API with structured prompts built from the analysis
pipeline output. Falls back to rule-based feedback generation if the
API call fails (network error, rate limit, invalid key, etc.).
"""

import logging
from typing import Any

import openai

from app.agents.base_agent import BaseAgent
from app.config import settings

logger = logging.getLogger(__name__)

# ─── System Prompt ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert resume coach with 10+ years of experience in tech hiring, \
ATS optimization, and career development. You have reviewed thousands of resumes across all \
seniority levels. Your feedback is specific, actionable, and encouraging.

Given the resume analysis data below, provide:
1. A 2-3 sentence summary of the resume's overall quality.
2. A list of 3-5 specific, prioritized suggestions grouped by section.
3. A one-line tone assessment (e.g., "Professional but could be more concise").
4. An estimated score improvement if all suggestions are implemented.

Be direct and specific. Avoid generic advice. Reference the actual scores and data provided."""

USER_PROMPT_TEMPLATE = """## Resume Analysis Data

**Resume Score:** {resume_score}/100
**ATS Score:** {ats_score}/100

### Component Scores
{component_scores_text}

### Strengths
{strengths_text}

### Areas for Improvement
{improvements_text}

### Present Skills ({present_count})
{present_skills_text}

### Missing Skills (from Job Description)
{missing_skills_text}

### Top Career Predictions
{career_predictions_text}

---

Based on this analysis, provide your structured feedback."""


class FeedbackAgent(BaseAgent):
    """Generates AI-powered resume feedback using GPT-4o-mini.

    Falls back to deterministic rule-based feedback if the OpenAI
    API is unavailable or returns an error.
    """

    name: str = "feedback_agent"
    version: str = "1.0.0"

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Generate structured resume feedback.

        Args:
            input_data: Must contain:
                - resume_text (str): Full resume text.
                - scores (dict): Score data from ATSEvaluatorAgent.
                - missing_skills (list[str]): Skills missing from resume.
                - career_predictions (list[dict]): Career prediction data.
                - present_skills (list[str], optional): Skills found.
                - strengths (list[str], optional): Identified strengths.
                - improvements (list[str], optional): Identified improvements.

        Returns:
            Dict with summary_feedback, detailed_suggestions,
            tone_analysis, estimated_improvement, source.
        """
        logger.info("FeedbackAgent — generating resume feedback")

        # Try AI-powered feedback first
        try:
            result = await self._generate_ai_feedback(input_data)
            result["source"] = "openai_gpt4o_mini"
            logger.info("FeedbackAgent — AI feedback generated successfully")
            return result
        except Exception as exc:
            logger.warning(
                "FeedbackAgent — OpenAI API failed (%s), falling back to rule-based",
                type(exc).__name__,
            )
            result = self._generate_rule_based_feedback(input_data)
            result["source"] = "rule_based_fallback"
            return result

    async def _generate_ai_feedback(
        self, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate feedback using OpenAI GPT-4o-mini.

        Args:
            input_data: Pipeline analysis data.

        Returns:
            Structured feedback dict.

        Raises:
            openai.OpenAIError: On API failure.
            ValueError: If API key is not configured.
        """
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        # Build the user prompt from analysis data
        user_prompt = self._build_user_prompt(input_data)

        client = openai.AsyncOpenAI(api_key=api_key)

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
            temperature=0.3,
        )

        ai_text = response.choices[0].message.content or ""
        return self._parse_ai_response(ai_text, input_data)

    @staticmethod
    def _build_user_prompt(input_data: dict[str, Any]) -> str:
        """Build the user prompt from pipeline analysis data.

        Args:
            input_data: Analysis data from the pipeline.

        Returns:
            Formatted prompt string.
        """
        scores = input_data.get("scores", {})
        component_scores = scores.get("component_scores", {})
        present_skills = input_data.get("present_skills", [])
        missing_skills = input_data.get("missing_skills", [])
        career_predictions = input_data.get("career_predictions", [])
        strengths = input_data.get("strengths", [])
        improvements = input_data.get("improvements", [])

        # Format component scores
        comp_lines = []
        for name, value in component_scores.items():
            comp_lines.append(f"- {name.title()}: {value}")
        component_scores_text = "\n".join(comp_lines) or "- No component scores available"

        # Format career predictions
        pred_lines = []
        for pred in career_predictions[:3]:
            role = pred.get("role", "Unknown")
            confidence = pred.get("confidence", 0)
            match = pred.get("match_percentage", 0)
            pred_lines.append(f"- {role}: {match:.0f}% match (confidence: {confidence:.2f})")
        career_predictions_text = "\n".join(pred_lines) or "- No predictions available"

        return USER_PROMPT_TEMPLATE.format(
            resume_score=scores.get("total_score", 0),
            ats_score=scores.get("ats_score", 0),
            component_scores_text=component_scores_text,
            strengths_text="\n".join(f"- {s}" for s in strengths) or "- None identified",
            improvements_text="\n".join(f"- {i}" for i in improvements) or "- None identified",
            present_count=len(present_skills),
            present_skills_text=", ".join(present_skills[:20]) or "None found",
            missing_skills_text=", ".join(missing_skills[:10]) or "None (no job description provided)",
            career_predictions_text=career_predictions_text,
        )

    @staticmethod
    def _parse_ai_response(
        ai_text: str, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Parse GPT response into structured feedback.

        The AI response is kept as free-text summary_feedback.
        We extract structured suggestions deterministically from
        the pipeline data to ensure consistency.

        Args:
            ai_text: Raw text from GPT-4o-mini.
            input_data: Original pipeline data.

        Returns:
            Structured feedback dict.
        """
        scores = input_data.get("scores", {})
        total_score = scores.get("total_score", 0)
        improvements = input_data.get("improvements", [])

        # Build detailed suggestions from improvements
        section_map = {
            "summary": "Summary/Objective",
            "objective": "Summary/Objective",
            "skills": "Skills",
            "project": "Projects",
            "experience": "Experience",
            "format": "Formatting",
            "quantif": "Impact Metrics",
            "action verb": "Language",
            "short": "Length",
            "long": "Length",
        }

        detailed_suggestions: list[dict[str, str]] = []
        for improvement in improvements:
            section = "General"
            imp_lower = improvement.lower()
            for keyword, sect in section_map.items():
                if keyword in imp_lower:
                    section = sect
                    break
            detailed_suggestions.append({
                "section": section,
                "issue": improvement,
                "fix": _generate_fix_suggestion(improvement),
            })

        # Estimate potential improvement
        gap = 100 - total_score
        estimated_improvement = min(round(gap * 0.6), 35)  # realistic cap

        return {
            "summary_feedback": ai_text.strip(),
            "detailed_suggestions": detailed_suggestions,
            "tone_analysis": _analyze_tone(input_data),
            "estimated_improvement": estimated_improvement,
        }

    @staticmethod
    def _generate_rule_based_feedback(
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate deterministic feedback when AI is unavailable.

        Uses scores and improvements from the pipeline to construct
        feedback without any external API calls.

        Args:
            input_data: Pipeline analysis data.

        Returns:
            Structured feedback dict.
        """
        scores = input_data.get("scores", {})
        total_score = scores.get("total_score", 0)
        ats_score = scores.get("ats_score", 0)
        missing_skills = input_data.get("missing_skills", [])
        improvements = input_data.get("improvements", [])
        career_predictions = input_data.get("career_predictions", [])

        # Summary
        if total_score >= 80:
            quality = "strong"
            tone = "This resume is well-structured and impactful."
        elif total_score >= 60:
            quality = "good with room for improvement"
            tone = "The resume has a solid foundation but needs polish in key areas."
        elif total_score >= 40:
            quality = "average"
            tone = "The resume needs significant improvements to stand out to recruiters."
        else:
            quality = "below average"
            tone = "The resume requires a major overhaul to be competitive."

        summary_parts = [
            f"Your resume scored {total_score}/100 overall and {ats_score}/100 for ATS compatibility, "
            f"which is {quality}.",
        ]

        if missing_skills:
            summary_parts.append(
                f"There are {len(missing_skills)} skills from the job description "
                f"missing from your resume — adding these could significantly improve your match rate."
            )

        if career_predictions:
            top = career_predictions[0]
            summary_parts.append(
                f"Based on your skill profile, you're best suited for a "
                f"{top.get('role', 'technical')} role ({top.get('match_percentage', 0):.0f}% match)."
            )

        summary_feedback = " ".join(summary_parts)

        # Suggestions
        detailed_suggestions: list[dict[str, str]] = []
        for improvement in improvements[:5]:
            detailed_suggestions.append({
                "section": "General",
                "issue": improvement,
                "fix": _generate_fix_suggestion(improvement),
            })

        # Estimated improvement
        gap = 100 - total_score
        estimated_improvement = min(round(gap * 0.5), 30)

        return {
            "summary_feedback": summary_feedback,
            "detailed_suggestions": detailed_suggestions,
            "tone_analysis": tone,
            "estimated_improvement": estimated_improvement,
        }


# ─── Helper Functions ────────────────────────────────────────────────────────

def _generate_fix_suggestion(improvement: str) -> str:
    """Generate a specific fix suggestion for an improvement point.

    Args:
        improvement: The improvement description.

    Returns:
        Actionable fix suggestion string.
    """
    imp_lower = improvement.lower()

    if "summary" in imp_lower or "objective" in imp_lower:
        return (
            "Add a 2-3 sentence professional summary at the top. "
            "Start with your title, years of experience, and key specialization. "
            "Example: 'Senior Backend Engineer with 5+ years building scalable Python/FastAPI microservices.'"
        )
    if "skills" in imp_lower:
        return (
            "Create a dedicated 'Technical Skills' section grouped by category "
            "(Languages, Frameworks, Databases, Cloud, Tools). List 10-20 relevant skills."
        )
    if "project" in imp_lower:
        return (
            "Add 2-3 projects with: project name, 1-2 line description, "
            "technologies used, and a link to the repo or demo."
        )
    if "action verb" in imp_lower:
        return (
            "Start each bullet point with a strong action verb: "
            "'Developed', 'Implemented', 'Optimized', 'Reduced', 'Architected'."
        )
    if "quantif" in imp_lower or "metric" in imp_lower:
        return (
            "Add numbers to your achievements: 'Reduced API latency by 40%', "
            "'Managed a team of 8 engineers', 'Processed 1M+ daily transactions'."
        )
    if "short" in imp_lower:
        return "Expand your resume to 400-800 words with more detail on projects and experience."
    if "long" in imp_lower:
        return "Condense to 1-2 pages by removing outdated roles and tightening bullet points."
    if "experience" in imp_lower:
        return (
            "Add work experience entries with: Company, Title, Dates, "
            "and 3-5 bullet points per role using the STAR method."
        )
    if "format" in imp_lower or "header" in imp_lower:
        return (
            "Use standard section headers: Summary, Experience, Education, Skills, Projects. "
            "Avoid creative headers that ATS systems may not recognize."
        )

    return "Review this area and apply best practices from top-performing resumes in your field."


def _analyze_tone(input_data: dict[str, Any]) -> str:
    """Analyze the overall tone of the resume based on scores.

    Args:
        input_data: Pipeline analysis data.

    Returns:
        One-line tone assessment string.
    """
    scores = input_data.get("scores", {})
    component = scores.get("component_scores", {})

    exp_score = component.get("experience", 0)
    obj_score = component.get("objectives", 0)
    proj_score = component.get("projects", 0)

    if exp_score >= 8 and obj_score >= 20:
        return "Professional and results-oriented — strong executive tone"
    if proj_score >= 20 and obj_score < 15:
        return "Technical and project-focused — consider adding a professional summary for balance"
    if exp_score >= 5 and proj_score >= 15:
        return "Well-balanced between experience and projects — shows practical capability"
    if obj_score >= 15:
        return "Clear goals but could strengthen with more concrete examples and metrics"

    return "Needs more professional polish — focus on action verbs and quantifiable achievements"
