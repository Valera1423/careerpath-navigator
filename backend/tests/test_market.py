def test_market_trends_empty(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": [],
        },
    )
    r = client.get("/api/v1/market/trends", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["vacancies_analyzed"] == 0
    assert body["top_skills"] == []
    assert body["salaries"]["avg"] is None