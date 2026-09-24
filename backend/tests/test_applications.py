def test_application_lifecycle(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": [],
        },
    )
    r = client.post(
        "/api/v1/applications",
        json={
            "vacancy_id": "v-1",
            "vacancy_title": "Аналитик данных",
            "company": "Test Corp",
            "remind_in_days": 3,
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    app_id = r.json()["id"]
    assert r.json()["status"] == "applied"
    assert r.json()["remind_at"] is not None

    r2 = client.patch(
        f"/api/v1/applications/{app_id}",
        json={"status": "interview"},
        headers=auth_headers,
    )
    assert r2.json()["status"] == "interview"

    lst = client.get("/api/v1/applications", headers=auth_headers).json()
    assert len(lst) == 1

    client.delete(f"/api/v1/applications/{app_id}", headers=auth_headers)
    assert client.get("/api/v1/applications", headers=auth_headers).json() == []