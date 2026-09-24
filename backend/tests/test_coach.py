def test_coach_ask_falls_back_to_template(client, auth_headers):
    import respx
    from httpx import Response

    with respx.mock:
        respx.get(url__startswith="http://opendata.trudvsem.ru").mock(
            return_value=Response(200, json={"status": "200", "meta": {}, "vacancies": []})
        )
        client.post(
            "/api/v1/users/onboarding",
            json={
                "max_user_id": "test-user-1",
                "desired_position": "Аналитик данных",
                "experience": "none",
                "skills": ["excel"],
            },
        )
        r = client.post(
            "/api/v1/coach/ask",
            json={"question": "Зачем мне SQL?"},
            headers=auth_headers,
        )
        assert r.status_code == 200
        body = r.json()
        assert body["used_llm"] is False
        assert "SQL" in body["answer"] or "sql" in body["answer"]