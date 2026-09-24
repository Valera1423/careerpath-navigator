import io

import pytest


def _make_docx(text: str) -> bytes:
    from docx import Document

    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_resume_upload_extracts_skills(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": ["excel"],
        },
    )

    content = _make_docx(
        "Опыт: анализ данных на Python, написание SQL-запросов, "
        "работа с pandas и Power BI. Английский B2."
    )
    files = {"file": ("resume.docx", content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    r = client.post("/api/v1/users/me/resume", files=files, headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert "python" in body["added_skills"]
    assert "sql" in body["added_skills"]


def test_resume_upload_wrong_format(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": [],
        },
    )
    files = {"file": ("resume.txt", b"just text", "text/plain")}
    r = client.post("/api/v1/users/me/resume", files=files, headers=auth_headers)
    assert r.status_code == 400