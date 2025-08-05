def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_hello(client):
    response = client.get("/hello?name=Maude")
    assert response.status_code == 200
    assert response.json()["greeting"] == "Hello, Maude!"
