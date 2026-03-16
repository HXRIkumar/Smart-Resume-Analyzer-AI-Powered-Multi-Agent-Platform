"""Abstract base agent class for all AI agents."""

from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Base class for all resume analysis agents.

    Each agent receives context, processes it, and returns structured output.
    Agents are designed to be stateless and composable.
    """

    name: str = "base_agent"

    @abstractmethod
    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent's task.

        Args:
            context: Dictionary containing input data (resume text, job description, etc.)

        Returns:
            Dictionary containing the agent's output.
        """
        ...

    def validate_input(self, context: dict[str, Any], required_keys: list[str]) -> None:
        """Validate that required keys are present in context."""
        missing = [k for k in required_keys if k not in context]
        if missing:
            raise ValueError(f"Agent '{self.name}' missing required context keys: {missing}")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
