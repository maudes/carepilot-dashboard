def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_hello(client):
    response = client.get("/hello?name=Maude")
    assert response.status_code == 200
    assert response.json()["greeting"] == "Hello, Maude!"


def test_redis_client_ping(redis_client_ping):
    response = redis_client_ping.ping()
    assert response is True
