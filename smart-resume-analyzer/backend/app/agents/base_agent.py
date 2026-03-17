"""Base agent abstract class and AgentResult dataclass.

Provides the foundation for all agents in the multi-agent pipeline.
Every agent must inherit from BaseAgent and implement the async
process() method. All executions are wrapped in error handling and
produce a structured AgentResult with timing and logging.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


# ─── Agent Result ────────────────────────────────────────────────────────────

@dataclass
class AgentResult:
    """Structured result returned by every agent execution.

    Attributes:
        agent_name: Identifier of the agent that produced this result.
        success: Whether the agent completed without errors.
        output: The agent's output payload (dict of results).
        error: Error message if the agent failed, None otherwise.
        execution_ms: Wall-clock execution time in milliseconds.
        timestamp: ISO-8601 timestamp of when execution completed.
    """

    agent_name: str
    success: bool
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    execution_ms: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialize the result to a plain dictionary."""
        return asdict(self)

    def to_log_entry(self) -> dict[str, Any]:
        """Return a compact log entry suitable for the pipeline audit trail."""
        return {
            "agent": self.agent_name,
            "success": self.success,
            "execution_ms": round(self.execution_ms, 2),
            "timestamp": self.timestamp,
            "error": self.error,
        }


# ─── Base Agent ──────────────────────────────────────────────────────────────

class BaseAgent(ABC):
    """Abstract base class for all pipeline agents.

    Subclasses must set the `name` class attribute and implement the
    `process()` coroutine. The `execute()` method wraps `process()`
    with timing, logging, and error handling — callers should always
    use `execute()` rather than calling `process()` directly.

    Class Attributes:
        name: Unique identifier for this agent (e.g., 'parser_agent').
        version: Semantic version of the agent implementation.
    """

    name: str = "base_agent"
    version: str = "1.0.0"

    @abstractmethod
    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Core processing logic — subclasses must implement this.

        Args:
            input_data: Input payload from the pipeline context.

        Returns:
            Dict containing the agent's output data.
        """
        ...

    async def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """Execute the agent with full error handling, timing, and logging.

        This is the public entry point used by the pipeline orchestrator.
        It wraps `process()` and always returns an AgentResult, even on failure.

        Args:
            input_data: Input payload from the pipeline context.

        Returns:
            AgentResult with success/failure status, timing, and output.
        """
        start_time = time.perf_counter()
        try:
            logger.info("Agent '%s' v%s — starting execution", self.name, self.version)
            output = await self.process(input_data)
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            result = AgentResult(
                agent_name=self.name,
                success=True,
                output=output,
                execution_ms=elapsed_ms,
            )
            self._log_execution(result)
            return result

        except Exception as exc:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            error_msg = f"{type(exc).__name__}: {exc}"

            result = AgentResult(
                agent_name=self.name,
                success=False,
                output={},
                error=error_msg,
                execution_ms=elapsed_ms,
            )
            self._log_execution(result)
            return result

    def _log_execution(self, result: AgentResult) -> None:
        """Write structured execution log entry.

        Args:
            result: The AgentResult to log.
        """
        log_data = result.to_log_entry()
        if result.success:
            logger.info(
                "Agent '%s' — completed in %.1fms",
                result.agent_name,
                result.execution_ms,
                extra={"agent_log": log_data},
            )
        else:
            logger.error(
                "Agent '%s' — FAILED in %.1fms: %s",
                result.agent_name,
                result.execution_ms,
                result.error,
                extra={"agent_log": log_data},
            )
