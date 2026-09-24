def test_onboarding_requires_consent(client):
    r = client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "u-consent",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": [],
            "consent_pd": False,
        },
    )
    assert r.status_code == 422


def test_onboarding_stores_consent(client):
    r = client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "u-consent-2",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": [],
            "consent_pd": True,
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["consent_pd_given_at"] is not None
    assert body["employer_opt_in"] is False


def test_employer_opt_in_toggle(client):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "u-opt",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": ["sql"],
            "consent_pd": True,
        },
    )
    headers = {"X-Max-User-Id": "u-opt"}

    r = client.post(
        "/api/v1/users/me/employer-opt-in",
        json={"employer_opt_in": True},
        headers=headers,
    )
    assert r.json()["employer_opt_in"] is True

    r2 = client.post(
        "/api/v1/users/me/employer-opt-in",
        json={"employer_opt_in": False},
        headers=headers,
    )
    assert r2.json()["employer_opt_in"] is False


def test_employer_search_excludes_opt_out(client):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "u-hidden",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": ["sql"],
            "consent_pd": True,
        },
    )
    # регистрируем работодателя
    import os
    os.environ["ADMIN_SECRET"] = "test"
    r = client.post(
        "/api/v1/employer/v1/employers/register",
        headers={"X-Admin-Secret": "test"},
        json={"company_name": "X", "contact_email": "x@test.ru"},
    )
    if r.status_code == 200:
        key = r.json()["api_key"]
        r2 = client.get(
            "/api/v1/employer/v1/candidates/search?position=Аналитик",
            headers={"X-API-Key": key},
        )
        # opt-in по умолчанию false → пользователь не должен быть в выдаче
        assert r2.json()["total"] == 0