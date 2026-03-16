"""Parser agent — PDF text extraction."""

from typing import Any

import pdfplumber

from app.agents.base_agent import BaseAgent


class ParserAgent(BaseAgent):
    """Extracts text from PDF resume files using pdfplumber."""

    name = "parser_agent"

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Extract text from a PDF file.

        Args:
            context: Must contain 'file_path' key.

        Returns:
            Dict with 'raw_text' and 'page_count'.
        """
        self.validate_input(context, ["file_path"])
        file_path = context["file_path"]

        text_pages: list[str] = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_pages.append(page_text)

        raw_text = "\n\n".join(text_pages)
        return {
            "raw_text": raw_text,
            "page_count": len(text_pages),
        }
