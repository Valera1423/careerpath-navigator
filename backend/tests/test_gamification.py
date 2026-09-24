def test_progress_created_on_first_request(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": [],
        },
    )
    r = client.get("/api/v1/gamification/progress", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["xp"] == 0
    assert body["level"] == "intern"
    assert body["streak_days"] == 0


def test_xp_awarded_on_step_toggle(client, auth_headers):
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
                "skills": [],
            },
        )
        r = client.post("/api/v1/plan/regenerate", headers=auth_headers)
        step_id = r.json()["steps"][0]["id"]

        client.post(f"/api/v1/plan/steps/{step_id}/toggle", headers=auth_headers)

        progress = client.get("/api/v1/gamification/progress", headers=auth_headers).json()
        assert progress["xp"] == 50


def test_first_step_achievement(client, auth_headers):
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
                "skills": [],
            },
        )
        r = client.post("/api/v1/plan/regenerate", headers=auth_headers)
        step_id = r.json()["steps"][0]["id"]
        client.post(f"/api/v1/plan/steps/{step_id}/toggle", headers=auth_headers)

        achievements = client.get(
            "/api/v1/gamification/achievements", headers=auth_headers
        ).json()
        codes = {a["code"] for a in achievements}
        assert "first_step" in codes