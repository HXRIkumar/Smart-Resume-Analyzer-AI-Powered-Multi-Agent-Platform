"""ParserAgent — extracts and structures text from resume PDF files.

Uses pdfplumber for high-fidelity text extraction. Detects standard
resume sections (Education, Experience, Skills, Projects, Certifications)
via regex header matching. Handles corrupted, empty, and password-protected PDFs.
"""

import logging
import re
import unicodedata
from typing import Any

import pdfplumber

from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# ─── Section Header Patterns ────────────────────────────────────────────────
SECTION_PATTERNS: dict[str, re.Pattern] = {
    "education": re.compile(
        r"^\s*(EDUCATION|ACADEMIC\s+BACKGROUND|ACADEMIC\s+QUALIFICATIONS|DEGREES?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "experience": re.compile(
        r"^\s*(WORK\s+EXPERIENCE|PROFESSIONAL\s+EXPERIENCE|EXPERIENCE|EMPLOYMENT\s+HISTORY|WORK\s+HISTORY)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "skills": re.compile(
        r"^\s*(SKILLS|TECHNICAL\s+SKILLS|CORE\s+COMPETENCIES|KEY\s+SKILLS|COMPETENCIES|TECHNOLOGIES)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "projects": re.compile(
        r"^\s*(PROJECTS|PERSONAL\s+PROJECTS|KEY\s+PROJECTS|ACADEMIC\s+PROJECTS|NOTABLE\s+PROJECTS)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "certifications": re.compile(
        r"^\s*(CERTIFICATIONS?|LICENSES?\s*(?:&|AND)?\s*CERTIFICATIONS?|PROFESSIONAL\s+CERTIFICATIONS?)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
    "summary": re.compile(
        r"^\s*(SUMMARY|PROFESSIONAL\s+SUMMARY|OBJECTIVE|CAREER\s+OBJECTIVE|PROFILE|ABOUT\s+ME)\s*$",
        re.IGNORECASE | re.MULTILINE,
    ),
}


class ParserAgent(BaseAgent):
    """Extracts structured text and sections from resume PDF files.

    Handles multi-page documents, normalizes unicode, removes excess
    whitespace, and detects standard resume sections.
    """

    name: str = "parser_agent"
    version: str = "1.0.0"

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Extract text from a PDF resume and detect sections.

        Args:
            input_data: Must contain 'file_path' (str) pointing to the PDF.

        Returns:
            Dict with keys: raw_text, sections, page_count, word_count, char_count.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
            ValueError: If the PDF is empty or password-protected.
            RuntimeError: If pdfplumber cannot parse the file.
        """
        file_path: str = input_data["file_path"]
        logger.info("ParserAgent — extracting text from: %s", file_path)

        # ── Extract raw text from all pages ──────────────────────────────
        raw_pages: list[str] = []
        try:
            with pdfplumber.open(file_path) as pdf:
                if pdf.is_encrypted:
                    raise ValueError(
                        f"Password-protected PDF cannot be parsed: {file_path}"
                    )

                page_count = len(pdf.pages)
                if page_count == 0:
                    raise ValueError(f"PDF has no pages: {file_path}")

                for page in pdf.pages:
                    text = page.extract_text() or ""
                    raw_pages.append(text)

        except pdfplumber.pdfminer.pdfparser.PDFSyntaxError as exc:
            raise RuntimeError(f"Corrupted or invalid PDF file: {exc}") from exc
        except FileNotFoundError:
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        except ValueError:
            raise  # Re-raise our own ValueError
        except Exception as exc:
            raise RuntimeError(
                f"Unexpected error reading PDF: {type(exc).__name__}: {exc}"
            ) from exc

        # ── Combine and clean text ───────────────────────────────────────
        combined_text = "\n\n".join(raw_pages)
        cleaned_text = self._clean_text(combined_text)

        if not cleaned_text.strip():
            raise ValueError(
                "PDF appears to be empty or contains only images/scanned content"
            )

        # ── Detect sections ──────────────────────────────────────────────
        sections = self._extract_sections(cleaned_text)

        # ── Compute stats ────────────────────────────────────────────────
        words = cleaned_text.split()
        word_count = len(words)

        logger.info(
            "ParserAgent — extracted %d pages, %d words, %d sections detected",
            page_count,
            word_count,
            sum(1 for v in sections.values() if v),
        )

        return {
            "raw_text": cleaned_text,
            "sections": sections,
            "page_count": page_count,
            "word_count": word_count,
            "char_count": len(cleaned_text),
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Normalize unicode, remove excessive whitespace, fix encoding artifacts.

        Args:
            text: Raw extracted text from PDF.

        Returns:
            Cleaned and normalized text string.
        """
        # Normalize unicode (NFD → NFC)
        text = unicodedata.normalize("NFC", text)

        # Replace common PDF artifacts
        text = text.replace("\x00", "")  # null bytes
        text = text.replace("\ufeff", "")  # BOM
        text = text.replace("\u2022", "•")  # bullet
        text = text.replace("\u2013", "–")  # en-dash
        text = text.replace("\u2014", "—")  # em-dash
        text = text.replace("\u2018", "'").replace("\u2019", "'")  # smart quotes
        text = text.replace("\u201c", '"').replace("\u201d", '"')

        # Collapse multiple blank lines into two newlines
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Collapse multiple spaces (but keep newlines)
        text = re.sub(r"[^\S\n]+", " ", text)

        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.splitlines()]
        text = "\n".join(lines)

        return text.strip()

    @staticmethod
    def _extract_sections(text: str) -> dict[str, str]:
        """Detect and extract standard resume sections.

        Uses regex patterns to find section headers, then captures
        all text between consecutive headers as the section content.

        Args:
            text: Cleaned resume text.

        Returns:
            Dict mapping section names to their content text.
            Missing sections map to empty strings.
        """
        # Find all section header positions
        found_headers: list[tuple[str, int, int]] = []  # (name, start, end)

        for section_name, pattern in SECTION_PATTERNS.items():
            for match in pattern.finditer(text):
                found_headers.append((section_name, match.start(), match.end()))

        # Sort by position in document
        found_headers.sort(key=lambda x: x[1])

        # Extract content between consecutive headers
        sections: dict[str, str] = {
            name: "" for name in SECTION_PATTERNS
        }

        for i, (name, _start, end) in enumerate(found_headers):
            # Content runs from end of this header to start of next header
            if i + 1 < len(found_headers):
                next_start = found_headers[i + 1][1]
                content = text[end:next_start].strip()
            else:
                content = text[end:].strip()

            sections[name] = content

        return sections
