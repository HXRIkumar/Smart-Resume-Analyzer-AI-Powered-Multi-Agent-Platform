"""ATS evaluator agent — Applicant Tracking System scoring."""

import re
from typing import Any

from app.agents.base_agent import BaseAgent


class ATSEvaluatorAgent(BaseAgent):
    """Evaluates resume for ATS compatibility and formatting issues."""

    name = "ats_evaluator_agent"

    # ATS best practice checks
    CHECKS = [
        {
            "id": "contact_info",
            "description": "Contact information present",
            "patterns": [r"\b[\w.+-]+@[\w-]+\.[\w.]+\b", r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"],
            "weight": 10,
        },
        {
            "id": "section_headers",
            "description": "Standard section headers",
            "patterns": [
                r"\b(experience|work\s+history)\b",
                r"\b(education|academic)\b",
                r"\b(skills|technical\s+skills)\b",
            ],
            "weight": 15,
        },
        {
            "id": "quantified_achievements",
            "description": "Quantified achievements",
            "patterns": [r"\d+%", r"\$\d+", r"\d+\+?\s*(years|months)", r"increased|decreased|improved|reduced"],
            "weight": 15,
        },
        {
            "id": "action_verbs",
            "description": "Action verbs used",
            "patterns": [
                r"\b(developed|managed|led|designed|implemented|created|built|optimized|delivered|achieved)\b"
            ],
            "weight": 10,
        },
        {
            "id": "appropriate_length",
            "description": "Appropriate resume length",
            "patterns": [],
            "weight": 10,
        },
    ]

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Evaluate resume for ATS compatibility.

        Args:
            context: Must contain 'raw_text' key.

        Returns:
            Dict with 'ats_score' and 'ats_issues'.
        """
        self.validate_input(context, ["raw_text"])
        raw_text = context["raw_text"]
        text_lower = raw_text.lower()

        total_weight = sum(c["weight"] for c in self.CHECKS)
        earned_weight = 0
        issues: list[dict[str, str]] = []

        for check in self.CHECKS:
            if check["id"] == "appropriate_length":
                word_count = len(raw_text.split())
                if 200 <= word_count <= 1200:
                    earned_weight += check["weight"]
                else:
                    severity = "high" if word_count < 100 or word_count > 2000 else "medium"
                    issues.append({
                        "issue": f"Resume length ({word_count} words) is outside optimal range (200-1200)",
                        "severity": severity,
                        "suggestion": "Aim for a concise resume between 200-1200 words.",
                    })
                continue

            passed = any(re.search(p, text_lower) for p in check["patterns"])
            if passed:
                earned_weight += check["weight"]
            else:
                issues.append({
                    "issue": f"Missing: {check['description']}",
                    "severity": "medium",
                    "suggestion": f"Consider adding {check['description'].lower()} to improve ATS compatibility.",
                })

        # Bonus for clean formatting (no excessive special characters)
        special_char_ratio = len(re.findall(r"[^\w\s.,;:/()\-@]", raw_text)) / max(len(raw_text), 1)
        if special_char_ratio < 0.02:
            earned_weight += 5
            total_weight += 5
        else:
            total_weight += 5
            issues.append({
                "issue": "Excessive special characters detected",
                "severity": "low",
                "suggestion": "Remove fancy formatting characters that may confuse ATS parsers.",
            })

        ats_score = round((earned_weight / total_weight) * 100, 1) if total_weight > 0 else 0

        return {
            "ats_score": ats_score,
            "ats_issues": issues,
        }
