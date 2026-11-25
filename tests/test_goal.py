DEFAULT_GOAL = "Be Happy & Be Healthy!"


def test_goal_requires_login(client):
    response = client.get("/api/goal/me")
    assert response.status_code == 401


def test_goal_flow(auth_client):
    # First read creates the default goal
    response = auth_client.get("/api/goal/me")
    assert response.status_code == 200
    assert response.json()["goal_text"] == DEFAULT_GOAL

    # Update, then read it back
    response = auth_client.put("/api/goal/me", json={"goal_text": "Walk daily"})
    assert response.status_code == 200
    assert response.json()["goal_text"] == "Walk daily"

    response = auth_client.get("/api/goal/me")
    assert response.json()["goal_text"] == "Walk daily"


def test_goal_update_rejects_empty(auth_client):
    response = auth_client.put("/api/goal/me", json={})
    assert response.status_code == 400
