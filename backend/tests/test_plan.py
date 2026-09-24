import respx
from httpx import Response


EMPTY_RESPONSE = {"status": "200", "meta": {"total": 0}, "vacancies": []}


@respx.mock
def test_plan_regenerate_and_toggle(client, auth_headers):
    respx.get(url__startswith="http://opendata.trudvsem.ru").mock(
        return_value=Response(200, json=EMPTY_RESPONSE)
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

    r = client.post("/api/v1/plan/regenerate", headers=auth_headers)
    assert r.status_code == 201
    steps = r.json()["steps"]
    assert len(steps) > 0
    assert r.json()["progress_percent"] == 0

    step_id = steps[0]["id"]
    r2 = client.post(f"/api/v1/plan/steps/{step_id}/toggle", headers=auth_headers)
    assert r2.status_code == 200
    assert r2.json()["is_done"] is True

    r3 = client.get("/api/v1/plan", headers=auth_headers)
    assert r3.json()["done"] == 1
    assert r3.json()["progress_percent"] > 0


@respx.mock
def test_toggle_foreign_step_returns_404(client, auth_headers):
    respx.get(url__startswith="http://opendata.trudvsem.ru").mock(
        return_value=Response(200, json=EMPTY_RESPONSE)
    )
    r = client.post("/api/v1/plan/steps/9999/toggle", headers=auth_headers)
    assert r.status_code == 404