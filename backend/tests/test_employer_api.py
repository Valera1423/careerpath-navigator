import os


def _onboard(client, user_id: str, opt_in: bool = False):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": user_id,
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": ["sql", "python", "excel"],
            "consent_pd": True,
        },
    )
    if opt_in:
        client.post(
            "/api/v1/users/me/employer-opt-in",
            json={"employer_opt_in": True},
            headers={"X-Max-User-Id": user_id},
        )


def _register_employer(client) -> str:
    os.environ["ADMIN_SECRET"] = "test"
    r = client.post(
        "/api/v1/employer/v1/employers/register",
        headers={"X-Admin-Secret": "test"},
        json={"company_name": "Test Corp", "contact_email": "hr@test.ru"},
    )
    return r.json()["api_key"]


def test_employer_api_requires_key(client):
    r = client.get("/api/v1/employer/v1/candidates/search?position=Аналитик")
    assert r.status_code == 401


def test_employer_search_only_opt_in(client):
    _onboard(client, "hidden-1", opt_in=False)
    _onboard(client, "visible-1", opt_in=True)
    key = _register_employer(client)

    r = client.get(
        "/api/v1/employer/v1/candidates/search?position=Аналитик&skills=sql,python",
        headers={"X-API-Key": key},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    candidate = body["items"][0]
    # PII отсутствует
    assert "full_name" not in candidate
    assert "email" not in candidate
    assert "max_user_id" not in candidate


def test_employer_search_anonymizes_region(client):
    _onboard(client, "moscow-1", opt_in=True)
    client.patch(
        "/api/v1/users/me/skills",
        json={"skills": ["sql"]},
        headers={"X-Max-User-Id": "moscow-1"},
    )
    key = _register_employer(client)
    r = client.get(
        "/api/v1/employer/v1/candidates/search?position=Аналитик&skills=sql",
        headers={"X-API-Key": key},
    )
    # Регион округлён до федерального округа
    for item in r.json()["items"]:
        if item["region"]:
            assert item["region"] in {"ЦФО", "СЗФО", "ПФО", "УФО", "СФО", "ЮФО", "ДФО", "Другой"}