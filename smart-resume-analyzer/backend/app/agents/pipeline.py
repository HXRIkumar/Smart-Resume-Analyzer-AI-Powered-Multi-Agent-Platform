"""AgentPipeline — orchestrates the 5-agent resume analysis pipeline.

Executes agents in sequence, feeding each agent's output into the next.
Tracks timing per agent, compiles a structured audit log, and handles
partial failures gracefully (failed agents are logged, pipeline continues).
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from app.agents.base_agent import AgentResult
from app.agents.parser_agent import ParserAgent
from app.agents.skill_analyzer_agent import SkillAnalyzerAgent
from app.agents.ats_evaluator_agent import ATSEvaluatorAgent
from app.agents.career_prediction_agent import CareerPredictionAgent
from app.agents.feedback_agent import FeedbackAgent

logger = logging.getLogger(__name__)


# ─── Pipeline Result ────────────────────────────────────────────────────────

@dataclass
class PipelineResult:
    """Aggregated result from the full 5-agent pipeline.

    Contains all data needed to populate the AnalysisResult database model.

    Attributes:
        resume_id: UUID of the resume being analyzed.
        success: True if pipeline completed (even with partial agent failures).
        resume_score: Overall resume quality score (0–100).
        ats_score: ATS compatibility score (0–100).
        ai_confidence: Average agent confidence (0.0–1.0).
        present_skills: Skills found in the resume.
        missing_skills: Skills missing relative to the job description.
        recommended_skills: Prioritized skill recommendations.
        strengths: Identified resume strengths.
        improvements: Improvement suggestions.
        career_predictions: Top career path predictions (JSON-serializable).
        keyword_heatmap: Skill → score mapping for UI visualization.
        ai_feedback_text: AI-generated feedback text.
        agent_pipeline_log: Structured audit trail (JSON-serializable).
        raw_text: Full extracted resume text.
        sections: Detected resume sections.
        total_execution_ms: Total pipeline execution time in milliseconds.
    """

    resume_id: UUID
    success: bool = True
    resume_score: int = 0
    ats_score: int = 0
    ai_confidence: float = 0.0
    present_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    recommended_skills: list[dict[str, Any]] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    career_predictions: dict[str, Any] = field(default_factory=dict)
    keyword_heatmap: dict[str, float] = field(default_factory=dict)
    ai_feedback_text: str = ""
    agent_pipeline_log: list[dict[str, Any]] = field(default_factory=list)
    raw_text: str = ""
    sections: dict[str, str] = field(default_factory=dict)
    total_execution_ms: float = 0.0


# ─── Pipeline Orchestrator ──────────────────────────────────────────────────

class AgentPipeline:
    """Orchestrates the sequential 5-agent resume analysis pipeline.

    Pipeline stages:
    1. ParserAgent — extract text and detect sections from PDF
    2. SkillAnalyzerAgent — NLP skill extraction and gap analysis
    3. ATSEvaluatorAgent — score resume quality and ATS compatibility
    4. CareerPredictionAgent — predict career paths from skill profile
    5. FeedbackAgent — generate AI-powered actionable feedback

    Each agent receives data from previous stages. If any agent fails,
    the pipeline logs the error and continues with partial data.
    """

    def __init__(self) -> None:
        """Instantiate all 5 pipeline agents."""
        self.parser = ParserAgent()
        self.skill_analyzer = SkillAnalyzerAgent()
        self.ats_evaluator = ATSEvaluatorAgent()
        self.career_predictor = CareerPredictionAgent()
        self.feedback = FeedbackAgent()

        logger.info(
            "AgentPipeline initialized with %d agents: %s",
            5,
            ", ".join([
                self.parser.name,
                self.skill_analyzer.name,
                self.ats_evaluator.name,
                self.career_predictor.name,
                self.feedback.name,
            ]),
        )

    async def run(
        self,
        file_path: str,
        job_description: str | None,
        resume_id: UUID,
    ) -> PipelineResult:
        """Execute the full analysis pipeline on a resume PDF.

        Args:
            file_path: Absolute path to the uploaded PDF file.
            job_description: Optional job description text for gap analysis.
            resume_id: UUID of the Resume record in the database.

        Returns:
            PipelineResult containing all analysis data and audit trail.
        """
        pipeline_start = time.perf_counter()
        pipeline_log: list[dict[str, Any]] = []
        result = PipelineResult(resume_id=resume_id)

        logger.info(
            "═══ Pipeline run started ═══ resume_id=%s, file=%s",
            resume_id, file_path,
        )

        # ────────────────────────────────────────────────────────────────
        # Stage 1: Parser Agent
        # ────────────────────────────────────────────────────────────────
        parser_result: AgentResult = await self.parser.execute({
            "file_path": file_path,
        })
        pipeline_log.append(parser_result.to_log_entry())

        if not parser_result.success:
            logger.error("Pipeline ABORTED — parser failed: %s", parser_result.error)
            result.success = False
            result.agent_pipeline_log = pipeline_log
            result.total_execution_ms = (time.perf_counter() - pipeline_start) * 1000
            return result

        raw_text: str = parser_result.output.get("raw_text", "")
        sections: dict[str, str] = parser_result.output.get("sections", {})
        result.raw_text = raw_text
        result.sections = sections

        # ────────────────────────────────────────────────────────────────
        # Stage 2: Skill Analyzer Agent
        # ────────────────────────────────────────────────────────────────
        skill_result: AgentResult = await self.skill_analyzer.execute({
            "text": raw_text,
            "job_description": job_description,
        })
        pipeline_log.append(skill_result.to_log_entry())

        present_skills: list[str] = []
        missing_skills: list[str] = []
        skill_scores: dict[str, float] = {}

        if skill_result.success:
            present_skills = skill_result.output.get("present_skills", [])
            missing_skills = skill_result.output.get("missing_skills", [])
            skill_scores = skill_result.output.get("skill_scores", {})
            result.present_skills = present_skills
            result.missing_skills = missing_skills
            result.recommended_skills = skill_result.output.get("recommended_skills", [])
            result.keyword_heatmap = skill_scores
        else:
            logger.warning("SkillAnalyzer failed — continuing with empty skills")

        # ────────────────────────────────────────────────────────────────
        # Stage 3: ATS Evaluator Agent
        # ────────────────────────────────────────────────────────────────
        ats_result: AgentResult = await self.ats_evaluator.execute({
            "text": raw_text,
            "sections": sections,
            "skills": present_skills,
        })
        pipeline_log.append(ats_result.to_log_entry())

        scores_data: dict[str, Any] = {}
        if ats_result.success:
            scores_data = ats_result.output
            result.resume_score = scores_data.get("total_score", 0)
            result.ats_score = scores_data.get("ats_score", 0)
            result.strengths = scores_data.get("strengths", [])
            result.improvements = scores_data.get("improvements", [])
        else:
            logger.warning("ATSEvaluator failed — continuing with zero scores")

        # ────────────────────────────────────────────────────────────────
        # Stage 4: Career Prediction Agent
        # ────────────────────────────────────────────────────────────────
        career_result: AgentResult = await self.career_predictor.execute({
            "present_skills": present_skills,
            "experience_text": sections.get("experience", ""),
        })
        pipeline_log.append(career_result.to_log_entry())

        career_predictions: list[dict[str, Any]] = []
        if career_result.success:
            career_predictions = career_result.output.get("predictions", [])
            result.career_predictions = career_result.output
        else:
            logger.warning("CareerPredictor failed — continuing without predictions")

        # ────────────────────────────────────────────────────────────────
        # Stage 5: Feedback Agent
        # ────────────────────────────────────────────────────────────────
        feedback_result: AgentResult = await self.feedback.execute({
            "resume_text": raw_text,
            "scores": scores_data,
            "missing_skills": missing_skills,
            "present_skills": present_skills,
            "career_predictions": career_predictions,
            "strengths": result.strengths,
            "improvements": result.improvements,
        })
        pipeline_log.append(feedback_result.to_log_entry())

        if feedback_result.success:
            result.ai_feedback_text = feedback_result.output.get("summary_feedback", "")
        else:
            logger.warning("FeedbackAgent failed — no AI feedback will be stored")

        # ────────────────────────────────────────────────────────────────
        # Finalize
        # ────────────────────────────────────────────────────────────────
        total_ms = (time.perf_counter() - pipeline_start) * 1000
        result.total_execution_ms = round(total_ms, 2)
        result.agent_pipeline_log = pipeline_log

        # Compute aggregate AI confidence from successful agents
        successful = [r for r in [
            parser_result, skill_result, ats_result, career_result, feedback_result
        ] if r.success]
        result.ai_confidence = round(len(successful) / 5, 2)

        # Check if any non-parser agent failed
        failed_agents = [
            entry["agent"] for entry in pipeline_log if not entry.get("success")
        ]
        if failed_agents:
            logger.warning(
                "Pipeline completed with %d failed agent(s): %s",
                len(failed_agents),
                ", ".join(failed_agents),
            )

        logger.info(
            "═══ Pipeline run completed ═══ resume_id=%s, score=%d, ats=%d, "
            "agents=%d/5 succeeded, total_ms=%.1f",
            resume_id,
            result.resume_score,
            result.ats_score,
            len(successful),
            total_ms,
        )

        return result
