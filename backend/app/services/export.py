"""Экспорт плана в PDF через reportlab (без системных зависимостей)."""
from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.models import PlanStep, User


def plan_to_pdf(user: User, steps: list[PlanStep]) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"План: {user.desired_position}")
    styles = getSampleStyleSheet()

    done = sum(1 for s in steps if s.is_done)
    story = [
        Paragraph(
            f"CareerPath Navigator — {user.desired_position}",
            styles["Title"],
        ),
        Paragraph(
            f"Регион: {user.region or '—'} · Опыт: {user.experience} · "
            f"Прогресс: {done}/{len(steps)}",
            styles["Normal"],
        ),
        Spacer(1, 12),
    ]

    for i, s in enumerate(steps, 1):
        mark = "[x]" if s.is_done else "[ ]"
        story.append(
            Paragraph(
                f"{mark} {i}. {s.title} <i>({s.skill})</i>",
                styles["Heading3"],
            )
        )
        story.append(Paragraph(s.description, styles["BodyText"]))
        if s.resource_url:
            story.append(
                Paragraph(
                    f'<a href="{s.resource_url}">{s.resource_url}</a>',
                    styles["BodyText"],
                )
            )
        story.append(Spacer(1, 8))

    doc.build(story)
    return buf.getvalue()