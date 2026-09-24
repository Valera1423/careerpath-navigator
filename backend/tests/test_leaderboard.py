def test_leaderboard_empty(client):
    r = client.get("/api/v1/leaderboard")
    assert r.status_code == 200
    assert r.json() == []