import respx
from httpx import Response


EMPTY_RESPONSE = {"status": "200", "meta": {"total": 0}, "vacancies": []}


@respx.mock
def test_recommendations_sorted_by_match_score(client, auth_headers):
    respx.get(url__startswith="http://opendata.trudvsem.ru").mock(
        return_value=Response(200, json=EMPTY_RESPONSE)
    )
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Python-разработчик",
            "experience": "none",
            "skills": ["python", "sql", "git"],
        },
    )
    r = client.get("/api/v1/vacancies/recommendations?limit=10", headers=auth_headers)
    assert r.status_code == 200
    items = r.json()["items"]
    if items:
        scores = [i["match_score"] for i in items]
        assert scores == sorted(scores, reverse=True)