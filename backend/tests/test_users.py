def test_me_requires_auth(client):
    assert client.get("/api/v1/users/me").status_code == 401


def test_me_unknown_user(client):
    r = client.get("/api/v1/users/me", headers={"X-Max-User-Id": "nope"})
    assert r.status_code == 404


def test_onboarding_creates_profile(client):
    payload = {
        "max_user_id": "test-user-1",
        "desired_position": "Аналитик данных",
        "region": "Москва",
        "experience": "none",
        "skills": ["excel", "python"],
    }
    r = client.post("/api/v1/users/onboarding", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["max_user_id"] == "test-user-1"
    assert sorted(body["skills"]) == ["excel", "python"]


def test_onboarding_short_position_returns_422(client):
    r = client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "u-2",
            "desired_position": "x",
            "experience": "none",
            "skills": [],
        },
    )
    assert r.status_code == 422


def test_onboarding_idempotent(client):
    payload = {
        "max_user_id": "test-user-1",
        "desired_position": "Аналитик данных",
        "experience": "none",
        "skills": ["excel"],
    }
    r1 = client.post("/api/v1/users/onboarding", json=payload)
    r2 = client.post("/api/v1/users/onboarding", json=payload)
    assert r1.json()["id"] == r2.json()["id"]


def test_update_skills(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": ["excel"],
        },
    )
    r = client.patch(
        "/api/v1/users/me/skills",
        json={"skills": ["excel", "python", "sql"]},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert sorted(r.json()["skills"]) == ["excel", "python", "sql"]