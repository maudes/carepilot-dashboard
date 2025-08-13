def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_hello(client):
    response = client.get("/hello?name=Maude")
    assert response.status_code == 200
    assert response.json()["greeting"] == "Hello, Maude!"


def test_redis_client(redis_client):
    redis_client.set("test:foo", "bar", ex=10)
    value = redis_client.get("test:foo")
    assert value == "bar"
