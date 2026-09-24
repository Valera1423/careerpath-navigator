def test_school_test_evaluate(client):
    r = client.get("/api/v1/school/questions")
    assert r.status_code == 200
    assert len(r.json()) == 18

    answers = {i: 2 for i in range(1, 7)}
    r2 = client.post("/api/v1/school/evaluate", json={"answers": answers})
    assert r2.status_code == 200
    body = r2.json()
    assert body["top_type"] in {"R", "I", "A", "S", "E", "C"}
    assert len(body["professions"]) >= 4


def test_day_in_life(client):
    r = client.get("/api/v1/school/day-in-life?profession=Аналитик данных")
    assert r.status_code == 200
    assert len(r.json()["timeline"]) > 0