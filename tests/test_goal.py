def test_goal_flow(client):
    response = client.get("api/goal/me")
    assert response .status_code == 200
    assert "goal_text" in response.json()
