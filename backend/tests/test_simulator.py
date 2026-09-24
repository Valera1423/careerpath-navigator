def test_simulator_happy_path(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": ["excel"],
            "consent_pd": True,
        },
    )

    r = client.post(
        "/api/v1/simulator/sessions?scenario_id=data_analyst_day",
        headers=auth_headers,
    )
    assert r.status_code == 201
    body = r.json()
    session_id = body["session_id"]
    assert body["node"]["type"] == "scenario"
    assert len(body["node"]["choices"]) > 0


def test_simulator_invalid_choice(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": [],
            "consent_pd": True,
        },
    )
    r = client.post(
        "/api/v1/simulator/sessions?scenario_id=data_analyst_day",
        headers=auth_headers,
    )
    session_id = r.json()["session_id"]

    r2 = client.post(
        f"/api/v1/simulator/sessions/{session_id}/choose",
        json={"choice_id": "nonexistent"},
        headers=auth_headers,
    )
    assert r2.status_code == 400


def test_simulator_full_run(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": ["excel"],
            "consent_pd": True,
        },
    )
    r = client.post(
        "/api/v1/simulator/sessions?scenario_id=data_analyst_day",
        headers=auth_headers,
    )
    session_id = r.json()["session_id"]

    # Идём по сценарию до конца
    choice = "check_sql"
    for _ in range(10):
        r = client.post(
            f"/api/v1/simulator/sessions/{session_id}/choose",
            json={"choice_id": choice},
            headers=auth_headers,
        )
        assert r.status_code == 200
        body = r.json()
        if body["is_finished"]:
            break
        # Берём первый доступный выбор на следующем узле
        choices = body["next"]["choices"]
        if choices:
            choice = choices[0]["id"]

    assert body["is_finished"] is True


def test_simulator_apply_to_profile(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": ["excel"],
            "consent_pd": True,
        },
    )
    r = client.post(
        "/api/v1/simulator/sessions?scenario_id=data_analyst_day",
        headers=auth_headers,
    )
    session_id = r.json()["session_id"]

    # Проходим сценарий с веткой, которая добавляет gap_skill
    client.post(
        f"/api/v1/simulator/sessions/{session_id}/choose",
        json={"choice_id": "guess"},
        headers=auth_headers,
    )

    r2 = client.post(
        f"/api/v1/simulator/sessions/{session_id}/apply-to-profile",
        headers=auth_headers,
    )
    assert r2.status_code == 200
    body = r2.json()
    assert "statistics" in body["added_skills"]