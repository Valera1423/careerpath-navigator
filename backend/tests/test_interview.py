def test_interview_full_session(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": [],
        },
    )
    r = client.post("/api/v1/interview/sessions", headers=auth_headers)
    assert r.status_code == 201
    body = r.json()
    session_id = body["session_id"]
    assert body["total"] == 5

    answer = (
        "Когда я делал проект по анализу продаж, нужно было выяснить, "
        "почему упала конверсия. Я выгрузил данные, сегментировал по устройствам "
        "и обнаружил проблему. В итоге удалось вернуть метрику."
    )

    for i in range(5):
        r = client.post(
            f"/api/v1/interview/sessions/{session_id}/answer",
            json={"answer": answer},
            headers=auth_headers,
        )
        assert r.status_code == 200
        if i == 4:
            assert r.json()["is_finished"] is True
            assert r.json()["next_question"] is None
        else:
            assert r.json()["next_question"] is not None


def test_interview_star_score(client):
    from app.services.interview import evaluate_answer

    good = evaluate_answer(
        "Когда я работал в команде над проектом, нужно было ускорить отчёты. "
        "Я написал скрипт на Python и автоматизировал выгрузку. "
        "В итоге время сократилось в 3 раза."
    )
    assert good.score >= 8

    bad = evaluate_answer("Ну, я что-то делал, было интересно.")
    assert bad.score <= 4