"""ATSEvaluatorAgent — scores resume for ATS compatibility and quality.

Implements a 5-category scoring rubric (objectives, skills, projects,
formatting, experience) plus ATS-specific checks (keyword density,
standard headers, no-graphics detection). Total score is 0–100.
"""

import logging
import re
from typing import Any

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# ─── Action Verbs for Objective/Experience Scoring ───────────────────────────
ACTION_VERBS: set[str] = {
    "achieved", "administered", "analyzed", "built", "collaborated",
    "created", "designed", "developed", "engineered", "established",
    "executed", "implemented", "improved", "increased", "integrated",
    "launched", "led", "managed", "mentored", "migrated",
    "monitored", "optimized", "orchestrated", "organized", "pioneered",
    "planned", "reduced", "refactored", "resolved", "scaled",
    "shipped", "simplified", "spearheaded", "streamlined", "supervised",
    "architected", "automated", "configured", "contributed", "coordinated",
    "debugged", "delivered", "deployed", "documented", "drove",
    "enhanced", "evaluated", "facilitated", "founded", "generated",
    "initiated", "innovated", "maintained", "modernized", "negotiated",
    "presented", "prioritized", "produced", "programmed", "proposed",
    "published", "rebuilt", "redesigned", "researched", "restructured",
    "revamped", "reviewed", "secured", "tested", "trained", "transformed",
    "troubleshot", "upgraded", "utilized", "visualized",
}

# ─── Standard ATS-Friendly Section Headers ───────────────────────────────────
STANDARD_HEADERS: list[str] = [
    "summary", "objective", "experience", "work experience",
    "professional experience", "education", "skills", "technical skills",
    "projects", "certifications", "awards", "publications",
    "volunteer", "interests", "references",
]

# ─── Metrics / Quantification Patterns ───────────────────────────────────────
METRICS_PATTERN = re.compile(
    r"\b\d+[%+]|\$\d+|\d+x|\b\d{1,3}(?:,\d{3})+\b|\b\d+\s*(?:users|customers|clients|projects|teams|members|employees|years|months|hours|requests|transactions)\b",
    re.IGNORECASE,
)


class ATSEvaluatorAgent(BaseAgent):
    """Evaluates resume quality and ATS compatibility.

    Scoring rubric:
    - Objectives/Summary: 0–25
    - Skills: 0–25
    - Projects: 0–25
    - Formatting: 0–15
    - Experience: 0–10
    Total: 0–100
    """

    name: str = "ats_evaluator_agent"
    version: str = "1.0.0"

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Evaluate resume for ATS compatibility and content quality.

        Args:
            input_data: Must contain:
                - text (str): Full resume text.
                - sections (dict): Extracted section contents.
                - skills (list[str]): Skills found by SkillAnalyzerAgent.

        Returns:
            Dict with total_score, ats_score, component_scores,
            strengths, improvements, missing_sections, keyword_density.
        """
        text: str = input_data["text"]
        sections: dict[str, str] = input_data.get("sections", {})
        skills: list[str] = input_data.get("skills", [])

        logger.info("ATSEvaluatorAgent — evaluating %d-char resume", len(text))

        # ── Score each component ─────────────────────────────────────────
        objectives_score = self._score_objectives(text, sections)
        skills_score = self._score_skills(sections, skills)
        projects_score = self._score_projects(text, sections)
        formatting_score = self._score_formatting(text, sections)
        experience_score = self._score_experience(text, sections)

        total_score = (
            objectives_score
            + skills_score
            + projects_score
            + formatting_score
            + experience_score
        )

        # ── ATS-specific score ───────────────────────────────────────────
        ats_score = self._compute_ats_score(text, sections, skills)

        # ── Strengths and improvements ───────────────────────────────────
        component_scores = {
            "objectives": objectives_score,
            "skills": skills_score,
            "projects": projects_score,
            "formatting": formatting_score,
            "experience": experience_score,
        }

        strengths = self._identify_strengths(component_scores, text)
        improvements = self._identify_improvements(component_scores, text, sections)
        missing_sections = self._find_missing_sections(sections)
        keyword_density = self._compute_keyword_density(text, skills)

        logger.info(
            "ATSEvaluatorAgent — total=%d, ats=%d, strengths=%d, improvements=%d",
            total_score, ats_score, len(strengths), len(improvements),
        )

        return {
            "total_score": min(total_score, 100),
            "ats_score": ats_score,
            "component_scores": component_scores,
            "strengths": strengths,
            "improvements": improvements,
            "missing_sections": missing_sections,
            "keyword_density": round(keyword_density, 4),
        }

    # ─── Objectives / Summary (0–25) ────────────────────────────────────

    @staticmethod
    def _score_objectives(text: str, sections: dict[str, str]) -> int:
        """Score the objectives/summary section (0–25).

        Criteria:
        - Has summary/objective section (8 pts)
        - Contains action verbs (7 pts)
        - Contains measurable impact / metrics (5 pts)
        - Appropriate length 2–5 sentences (5 pts)
        """
        score = 0
        summary = sections.get("summary", "")

        # Has summary section
        if summary:
            score += 8

            # Action verbs in summary
            summary_words = set(summary.lower().split())
            verb_count = len(summary_words & ACTION_VERBS)
            score += min(verb_count, 3) / 3 * 7

            # Measurable impact
            if METRICS_PATTERN.search(summary):
                score += 5

            # Length check (2–5 sentences)
            sentences = re.split(r"[.!?]+", summary)
            sentences = [s.strip() for s in sentences if s.strip()]
            if 2 <= len(sentences) <= 5:
                score += 5
            elif len(sentences) == 1:
                score += 2
        else:
            # Check if text starts with summary-like content
            first_200 = text[:200].lower()
            verb_count = sum(1 for v in ACTION_VERBS if v in first_200)
            score += min(verb_count, 2) * 2

        return min(round(score), 25)

    # ─── Skills (0–25) ──────────────────────────────────────────────────

    @staticmethod
    def _score_skills(sections: dict[str, str], skills: list[str]) -> int:
        """Score the skills section (0–25).

        Criteria:
        - Has dedicated skills section (8 pts)
        - Skill count >= 10 (7 pts)
        - Tech stack depth / variety (5 pts)
        - Skills are categorized (5 pts)
        """
        score = 0
        skills_text = sections.get("skills", "")

        # Has dedicated section
        if skills_text:
            score += 8

        # Skill count
        count = len(skills)
        if count >= 15:
            score += 7
        elif count >= 10:
            score += 5
        elif count >= 5:
            score += 3
        elif count > 0:
            score += 1

        # Tech stack depth (multiple categories)
        categories_found = 0
        skill_set_lower = {s.lower() for s in skills}
        lang_check = {"python", "javascript", "java", "c++", "go", "typescript"}
        fw_check = {"react", "django", "fastapi", "spring boot", "angular", "node.js"}
        db_check = {"postgresql", "mysql", "mongodb", "redis"}
        cloud_check = {"aws", "gcp", "azure", "docker", "kubernetes"}
        if skill_set_lower & lang_check:
            categories_found += 1
        if skill_set_lower & fw_check:
            categories_found += 1
        if skill_set_lower & db_check:
            categories_found += 1
        if skill_set_lower & cloud_check:
            categories_found += 1
        score += min(categories_found, 4) / 4 * 5

        # Categorization (colons, pipes, bullets suggest grouping)
        if skills_text and re.search(r"[:|•\-]", skills_text):
            score += 5
        elif skills_text:
            score += 2

        return min(round(score), 25)

    # ─── Projects (0–25) ────────────────────────────────────────────────

    @staticmethod
    def _score_projects(text: str, sections: dict[str, str]) -> int:
        """Score the projects section (0–25).

        Criteria:
        - Has projects section (8 pts)
        - Project descriptions exist (7 pts)
        - Links mentioned (github, demo, live) (5 pts)
        - Technologies mentioned per project (5 pts)
        """
        score = 0
        projects_text = sections.get("projects", "")

        # Has projects section
        if projects_text:
            score += 8

            # Descriptions (multiple lines = descriptions present)
            lines = [l.strip() for l in projects_text.split("\n") if l.strip()]
            if len(lines) >= 3:
                score += 7
            elif len(lines) >= 1:
                score += 3

            # Links
            link_pattern = re.compile(
                r"(?:github\.com|gitlab\.com|bitbucket\.org|https?://|www\.|\blink\b|\bdemo\b|\blive\b)",
                re.IGNORECASE,
            )
            if link_pattern.search(projects_text):
                score += 5

            # Technologies per project
            tech_mentions = re.findall(
                r"\b(?:using|built with|technologies?|stack|tools?)\s*[:\-]?\s*",
                projects_text,
                re.IGNORECASE,
            )
            if tech_mentions:
                score += 5
            elif any(char in projects_text for char in [",", "•", "|"]):
                score += 2
        else:
            # Check full text for project indicators
            if re.search(r"(?i)\bproject\b", text):
                score += 3

        return min(round(score), 25)

    # ─── Formatting (0–15) ──────────────────────────────────────────────

    @staticmethod
    def _score_formatting(text: str, sections: dict[str, str]) -> int:
        """Score formatting and structure (0–15).

        Criteria:
        - Consistent structure / standard headers (5 pts)
        - Appropriate length 300–1500 words (5 pts)
        - No images/tables indicators (5 pts)
        """
        score = 0

        # Standard headers found
        text_lower = text.lower()
        headers_found = sum(
            1 for h in STANDARD_HEADERS
            if re.search(rf"(?m)^\s*{re.escape(h)}\s*$", text_lower)
        )
        score += min(headers_found / 4, 1.0) * 5

        # Word count (ideal: 300–1500)
        word_count = len(text.split())
        if 300 <= word_count <= 1500:
            score += 5
        elif 200 <= word_count <= 2000:
            score += 3
        elif word_count > 0:
            score += 1

        # No image/table indicators (ATS can't parse these)
        bad_indicators = [
            r"\[image\]", r"\[table\]", r"\[chart\]", r"\[figure\]",
            r"<img", r"<table",
        ]
        has_bad = any(re.search(p, text_lower) for p in bad_indicators)
        score += 0 if has_bad else 5

        return min(round(score), 15)

    # ─── Experience (0–10) ──────────────────────────────────────────────

    @staticmethod
    def _score_experience(text: str, sections: dict[str, str]) -> int:
        """Score work experience section (0–10).

        Criteria:
        - Has experience section (4 pts)
        - Dates present (3 pts)
        - Role descriptions with action verbs (3 pts)
        """
        score = 0
        exp_text = sections.get("experience", "")

        # Has experience section
        if exp_text:
            score += 4

            # Dates present (YYYY, Month YYYY, MM/YYYY, etc.)
            date_pattern = re.compile(
                r"\b(?:19|20)\d{2}\b|"
                r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|"
                r"\b\d{1,2}/\d{4}\b|"
                r"\b(?:Present|Current)\b",
                re.IGNORECASE,
            )
            if date_pattern.search(exp_text):
                score += 3

            # Action verbs in experience
            exp_words = set(exp_text.lower().split())
            verb_count = len(exp_words & ACTION_VERBS)
            if verb_count >= 5:
                score += 3
            elif verb_count >= 2:
                score += 2
            elif verb_count >= 1:
                score += 1
        else:
            # Check full text for experience indicators
            if re.search(r"(?i)\b(?:work|experience|employed|position|role)\b", text):
                score += 2

        return min(round(score), 10)

    # ─── ATS-Specific Score ─────────────────────────────────────────────

    @staticmethod
    def _compute_ats_score(
        text: str, sections: dict[str, str], skills: list[str]
    ) -> int:
        """Compute ATS-specific compatibility score (0–100).

        Factors:
        - Keyword density (25%)
        - Standard header usage (25%)
        - No non-parseable elements (25%)
        - Contact info present (25%)
        """
        score = 0
        text_lower = text.lower()
        words = text_lower.split()
        word_count = max(len(words), 1)

        # Keyword density (skill terms / total words)
        skill_word_count = sum(
            text_lower.count(s.lower()) for s in skills
        )
        density = skill_word_count / word_count
        if 0.02 <= density <= 0.08:
            score += 25  # ideal range
        elif density > 0:
            score += 15

        # Standard headers
        headers_found = sum(
            1 for h in STANDARD_HEADERS
            if h in text_lower
        )
        score += min(headers_found / 5, 1.0) * 25

        # No images/tables/graphics
        bad_patterns = [r"<img", r"<table", r"\[image\]", r"\[figure\]"]
        has_graphics = any(re.search(p, text_lower) for p in bad_patterns)
        score += 0 if has_graphics else 25

        # Contact info (email, phone)
        has_email = bool(re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text))
        has_phone = bool(re.search(r"[\+]?\d[\d\s\-().]{7,}\d", text))
        contact_score = 0
        if has_email:
            contact_score += 12
        if has_phone:
            contact_score += 13
        score += contact_score

        return min(round(score), 100)

    # ─── Strengths & Improvements ────────────────────────────────────────

    @staticmethod
    def _identify_strengths(
        component_scores: dict[str, int], text: str
    ) -> list[str]:
        """Identify resume strengths based on scores.

        Args:
            component_scores: Dict of component name → score.
            text: Full resume text.

        Returns:
            List of strength descriptions.
        """
        strengths: list[str] = []
        thresholds = {
            "objectives": (20, "Strong professional summary with clear career goals"),
            "skills": (20, "Comprehensive and well-organized skills section"),
            "projects": (20, "Detailed projects with descriptions and links"),
            "formatting": (12, "Clean, ATS-friendly formatting and structure"),
            "experience": (8, "Well-documented work experience with measurable impact"),
        }
        for component, (threshold, msg) in thresholds.items():
            if component_scores.get(component, 0) >= threshold:
                strengths.append(msg)

        # Additional content checks
        if METRICS_PATTERN.search(text):
            strengths.append("Uses quantifiable metrics to demonstrate impact")
        if re.search(r"(?i)github\.com|gitlab\.com|portfolio", text):
            strengths.append("Includes portfolio or code repository links")

        return strengths

    @staticmethod
    def _identify_improvements(
        component_scores: dict[str, int],
        text: str,
        sections: dict[str, str],
    ) -> list[str]:
        """Identify areas for improvement based on scores.

        Args:
            component_scores: Dict of component name → score.
            text: Full resume text.
            sections: Extracted resume sections.

        Returns:
            List of improvement suggestions.
        """
        improvements: list[str] = []

        if component_scores.get("objectives", 0) < 10:
            improvements.append("Add a professional summary or career objective at the top")

        if component_scores.get("skills", 0) < 10:
            improvements.append("Create a dedicated skills section with categorized technical skills")

        if component_scores.get("projects", 0) < 10:
            improvements.append("Add a projects section with descriptions, technologies used, and links")

        if component_scores.get("formatting", 0) < 8:
            improvements.append("Use standard section headers (Education, Experience, Skills) for ATS compatibility")

        if component_scores.get("experience", 0) < 5:
            improvements.append("Add work experience with dates, roles, and achievement-focused bullet points")

        # Content-specific checks
        if not METRICS_PATTERN.search(text):
            improvements.append("Include quantifiable achievements (e.g., 'Improved performance by 40%')")

        text_lower = text.lower()
        action_count = sum(1 for v in ACTION_VERBS if v in text_lower)
        if action_count < 5:
            improvements.append("Use more action verbs (e.g., 'Developed', 'Implemented', 'Optimized')")

        word_count = len(text.split())
        if word_count < 250:
            improvements.append("Resume appears too short — aim for 400–800 words for a single-page resume")
        elif word_count > 1500:
            improvements.append("Resume may be too long — consider condensing to 1–2 pages")

        return improvements

    @staticmethod
    def _find_missing_sections(sections: dict[str, str]) -> list[str]:
        """Identify standard resume sections that are missing.

        Args:
            sections: Extracted resume sections.

        Returns:
            List of missing section names.
        """
        essential = ["summary", "experience", "education", "skills"]
        missing = [s.title() for s in essential if not sections.get(s)]
        return missing

    @staticmethod
    def _compute_keyword_density(text: str, skills: list[str]) -> float:
        """Compute keyword density (skill mentions / total words).

        Args:
            text: Full resume text.
            skills: List of found skills.

        Returns:
            Keyword density as a float (0.0–1.0).
        """
        words = text.split()
        if not words:
            return 0.0
        text_lower = text.lower()
        skill_mentions = sum(text_lower.count(s.lower()) for s in skills)
        return skill_mentions / len(words)
