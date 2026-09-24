def test_compass_graph(client, auth_headers):
    client.post(
        "/api/v1/users/onboarding",
        json={
            "max_user_id": "test-user-1",
            "desired_position": "Аналитик данных",
            "experience": "none",
            "skills": ["python"],
        },
    )
    r = client.get("/api/v1/compass/graph", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert "nodes" in body
    assert "edges" in body
    statuses = {n["id"]: n["data"]["status"] for n in body["nodes"]}
    assert statuses.get("python") == "done"
    assert statuses.get("sql") == "missing"