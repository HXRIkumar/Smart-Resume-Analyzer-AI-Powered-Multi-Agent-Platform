import logging
import pdfplumber
from app.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ParserAgent(BaseAgent):
    name = "parser_agent"
    version = "1.0.0"

    async def process(self, input_data: dict) -> dict:
        file_path = input_data.get("file_path")
        if not file_path:
            raise ValueError("No file_path provided")

        text_pages = []
        sections = {"education": "", "experience": "", "skills": "", "projects": "", "certifications": ""}

        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_pages.append(text)

        full_text = "\n".join(text_pages)

        section_headers = {
            "education": ["education", "academic"],
            "experience": ["experience", "work history", "employment"],
            "skills": ["skills", "technical skills", "technologies"],
            "projects": ["projects", "personal projects"],
            "certifications": ["certifications", "certificates", "licenses"]
        }

        lines = full_text.split("\n")
        current_section = None
        section_content = {k: [] for k in sections}

        for line in lines:
            line_lower = line.lower().strip()
            matched = False
            for section, keywords in section_headers.items():
                if any(kw in line_lower for kw in keywords):
                    current_section = section
                    matched = True
                    break
            if not matched and current_section:
                section_content[current_section].append(line)

        for k in sections:
            sections[k] = "\n".join(section_content[k])

        return {
            "raw_text": full_text,
            "sections": sections,
            "page_count": page_count,
            "word_count": len(full_text.split())
        }
