"""FeedbackAgent — generates actionable resume feedback via Google Gemini.

Calls the Google Gemini 1.5 Flash API with a structured prompt built from
the analysis pipeline output. Falls back to rule-based feedback generation
if the API call fails (network error, rate limit, invalid key, etc.).
"""

import json
import logging
import os
from typing import Any

import google.generativeai as genai

from app.agents.base_agent import BaseAgent
from app.config import settings

logger = logging.getLogger(__name__)

# ─── Prompt Template ────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """You are an expert resume coach with 10+ years of experience in tech hiring, \
ATS optimization, and career development. You have reviewed thousands of resumes across all \
seniority levels. Your feedback is specific, actionable, and encouraging.

Resume analysis data:
- Overall score: {resume_score}/100
- ATS score: {ats_score}/100
- Component scores: {component_scores_text}
- Strengths: {strengths_text}
- Areas for improvement: {improvements_text}
- Present skills ({present_count}): {present_skills_text}
- Missing skills (from job description): {missing_skills_text}
- Top career predictions: {career_predictions_text}
- Resume text excerpt: {resume_excerpt}

Provide:
1. A 2-3 sentence summary of the resume's overall quality
2. Three specific improvement suggestions with section, issue, and fix
3. A one-line tone assessment
4. Estimated score improvement if all changes are made

Reply in this JSON format ONLY — no markdown, no code fences, just raw JSON:
{{"summary_feedback": "...", "detailed_suggestions": [{{"section": "...", "issue": "...", "fix": "..."}}], "tone_analysis": "...", "estimated_improvement": 5}}"""


class FeedbackAgent(BaseAgent):
    """Generates AI-powered resume feedback using Google Gemini 1.5 Flash.

    Falls back to deterministic rule-based feedback if the Gemini
    API is unavailable or returns an error.
    """

    name: str = "feedback_agent"
    version: str = "2.0.0"

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
        logger.info("FeedbackAgent — generating resume feedback via Gemini")

        # Try AI-powered feedback first
        try:
            result = await self._generate_ai_feedback(input_data)
            result["source"] = "google_gemini_flash"
            logger.info("FeedbackAgent — Gemini feedback generated successfully")
            return result
        except Exception as exc:
            logger.warning(
                "FeedbackAgent — Gemini API failed (%s: %s), falling back to rule-based",
                type(exc).__name__,
                str(exc),
            )
            result = self._generate_rule_based_feedback(input_data)
            result["source"] = "rule_based_fallback"
            return result

    async def _generate_ai_feedback(
        self, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate feedback using Google Gemini 1.5 Flash.

        Args:
            input_data: Pipeline analysis data.

        Returns:
            Structured feedback dict.

        Raises:
            ValueError: If GEMINI_API_KEY is not configured.
            Exception: On Gemini API failure.
        """
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        # Configure and call the Gemini API
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt_text = self._build_prompt(input_data)

        response = model.generate_content(prompt_text)
        result_text = response.text

        logger.info("FeedbackAgent — received %d-char response from Gemini", len(result_text))
        return self._parse_ai_response(result_text, input_data)

    @staticmethod
    def _build_prompt(input_data: dict[str, Any]) -> str:
        """Build the Gemini prompt from pipeline analysis data.

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
        resume_text = input_data.get("resume_text", "")

        # Format component scores
        comp_lines = []
        for name, value in component_scores.items():
            comp_lines.append(f"{name.title()}: {value}")
        component_scores_text = ", ".join(comp_lines) or "No component scores available"

        # Format career predictions
        pred_lines = []
        for pred in career_predictions[:3]:
            role = pred.get("role", "Unknown")
            match = pred.get("match_percentage", 0)
            pred_lines.append(f"{role} ({match:.0f}% match)")
        career_predictions_text = ", ".join(pred_lines) or "No predictions available"

        return PROMPT_TEMPLATE.format(
            resume_score=scores.get("total_score", 0),
            ats_score=scores.get("ats_score", 0),
            component_scores_text=component_scores_text,
            strengths_text=", ".join(strengths) or "None identified",
            improvements_text=", ".join(improvements) or "None identified",
            present_count=len(present_skills),
            present_skills_text=", ".join(present_skills[:20]) or "None found",
            missing_skills_text=", ".join(missing_skills[:10]) or "None (no job description provided)",
            career_predictions_text=career_predictions_text,
            resume_excerpt=resume_text[:800],
        )

    @staticmethod
    def _parse_ai_response(
        ai_text: str, input_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Parse Gemini response into structured feedback.

        Attempts to parse the JSON response. Falls back to using the
        raw text as summary_feedback if JSON parsing fails.

        Args:
            ai_text: Raw text from Gemini 1.5 Flash.
            input_data: Original pipeline data.

        Returns:
            Structured feedback dict.
        """
        scores = input_data.get("scores", {})
        total_score = scores.get("total_score", 0)

        # Try to parse JSON from the response
        try:
            # Strip markdown code fences if present
            cleaned = ai_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                # Remove language identifier if present (e.g., "json")
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

            parsed = json.loads(cleaned)

            return {
                "summary_feedback": parsed.get("summary_feedback", ai_text.strip()),
                "detailed_suggestions": parsed.get("detailed_suggestions", []),
                "tone_analysis": parsed.get("tone_analysis", ""),
                "estimated_improvement": parsed.get("estimated_improvement", 0),
            }
        except (json.JSONDecodeError, KeyError, TypeError):
            logger.warning("FeedbackAgent — failed to parse Gemini JSON, using raw text")

            # Fallback: use the raw AI text as the summary
            gap = 100 - total_score
            return {
                "summary_feedback": ai_text.strip(),
                "detailed_suggestions": [],
                "tone_analysis": "",
                "estimated_improvement": min(round(gap * 0.5), 30),
            }

    @staticmethod
    def _generate_rule_based_feedback(
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate deterministic feedback when Gemini is unavailable.

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
            tone = "Professional and results-oriented resume with strong impact"
        elif total_score >= 60:
            quality = "good with room for improvement"
            tone = "Solid foundation but needs polish in key areas"
        elif total_score >= 40:
            quality = "average"
            tone = "Needs significant improvements to stand out to recruiters"
        else:
            quality = "below average"
            tone = "Requires a major overhaul to be competitive"

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

        # Build detailed suggestions from improvements
        detailed_suggestions: list[dict[str, str]] = []
        for improvement in improvements[:3]:
            detailed_suggestions.append({
                "section": _classify_section(improvement),
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

def _classify_section(improvement: str) -> str:
    """Classify an improvement suggestion into a resume section.

    Args:
        improvement: The improvement description text.

    Returns:
        Section name string.
    """
    imp_lower = improvement.lower()
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
    for keyword, section in section_map.items():
        if keyword in imp_lower:
            return section
    return "General"


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
            "Start with your title, years of experience, and key specialization."
        )
    if "skills" in imp_lower:
        return (
            "Create a dedicated 'Technical Skills' section grouped by category "
            "(Languages, Frameworks, Databases, Cloud, Tools). List 10-20 relevant skills."
        )
    if "project" in imp_lower:
        return (
            "Add 2-3 projects with: project name, description, "
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
