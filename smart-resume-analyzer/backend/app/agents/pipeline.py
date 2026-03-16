"""Agent pipeline — orchestrates all agents in sequence."""

import json
from typing import Any

from app.agents.parser_agent import ParserAgent
from app.agents.skill_analyzer_agent import SkillAnalyzerAgent
from app.agents.ats_evaluator_agent import ATSEvaluatorAgent
from app.agents.feedback_agent import FeedbackAgent
from app.agents.career_prediction_agent import CareerPredictionAgent


class AgentPipeline:
    """Orchestrates the multi-agent resume analysis pipeline.

    Pipeline flow:
    1. ParserAgent → Extract text from PDF
    2. SkillAnalyzerAgent → Extract and categorize skills
    3. ATSEvaluatorAgent → Score ATS compatibility
    4. FeedbackAgent → Generate LLM feedback
    5. CareerPredictionAgent → Predict career paths

    Each agent receives the accumulated context from previous agents.
    """

    def __init__(self):
        self.agents = [
            ParserAgent(),
            SkillAnalyzerAgent(),
            ATSEvaluatorAgent(),
            FeedbackAgent(),
            CareerPredictionAgent(),
        ]

    async def execute(
        self,
        resume_path: str,
        resume_text: str | None = None,
        job_description: str | None = None,
    ) -> dict[str, Any]:
        """Execute the full analysis pipeline.

        Args:
            resume_path: Path to the PDF file on disk.
            resume_text: Pre-extracted text (skip parser if provided).
            job_description: Optional job description for matching.

        Returns:
            Aggregated results from all agents.
        """
        # Initialize context
        context: dict[str, Any] = {
            "file_path": resume_path,
            "job_description": job_description,
        }

        if resume_text:
            context["raw_text"] = resume_text

        aggregated: dict[str, Any] = {}

        for agent in self.agents:
            # Skip parser if we already have text
            if agent.name == "parser_agent" and "raw_text" in context:
                continue

            try:
                result = await agent.execute(context)
                # Merge result into context for downstream agents
                context.update(result)
                aggregated.update(result)
            except Exception as e:
                aggregated[f"{agent.name}_error"] = str(e)

        # Compute overall score
        ats = aggregated.get("ats_score", 0)
        skill = aggregated.get("skill_match_score", len(aggregated.get("extracted_skills", [])) * 2)
        overall = min(round((ats * 0.4 + min(skill, 100) * 0.6), 1), 100)

        aggregated["overall_score"] = overall
        aggregated["skill_match_score"] = min(skill, 100)

        return aggregated
