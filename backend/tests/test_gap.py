import respx
from httpx import Response


EMPTY_RESPONSE = {"status": "200", "meta": {"total": 0}, "vacancies": []}


def _onboard(client):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "region": "Москва",
            "experience": "none",
            "skills": ["excel", "python"],
        },
    )


@respx.mock
def test_gap_falls_back_when_trudvsem_down(client, auth_headers):
    respx.get(url__startswith="http://opendata.trudvsem.ru").mock(
        return_value=Response(500)
    )
    _onboard(client)
    r = client.get("/api/v1/skills/gap", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "fallback"
    assert body["vacancies_analyzed"] > 0
    assert 0 <= body["readiness_score"] <= 100


@respx.mock
def test_gap_returns_missing_skills(client, auth_headers):
    respx.get(url__startswith="http://opendata.trudvsem.ru").mock(
        return_value=Response(200, json=EMPTY_RESPONSE)
    )
    _onboard(client)
    r = client.get("/api/v1/skills/gap", headers=auth_headers)
    missing = [i["skill"] for i in r.json()["missing"]]
    assert "sql" in missing
    assert "statistics" in missing