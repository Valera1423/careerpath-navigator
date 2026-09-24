"""Парсинг резюме PDF/DOCX с извлечением навыков."""
from __future__ import annotations

import io

from docx import Document
from pypdf import PdfReader

from app.services.skills import extract_skills

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ


def extract_text(filename: str, content: bytes) -> str:
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("Файл больше 5 МБ")

    lower = filename.lower()
    if lower.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    if lower.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Поддерживаются только PDF и DOCX")


def extract_skills_from_resume(filename: str, content: bytes) -> list[str]:
    text = extract_text(filename, content)
    return sorted(extract_skills(text))