import pytest
from backend.services.otp import otp_generator
from backend.services.redis_otp import (
    store_otp,
    delete_otp,
    fetch_otp,
    verify_otp
)


# Basic app check
def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_hello(client):
    response = client.get("/hello?name=Maude")
    assert response.status_code == 200
    assert response.json()["greeting"] == "Hello, Maude!"


# OTP generation test
def test_otp_generation():
    otp = otp_generator()
    assert type(otp) == str
    assert len(otp) == 8


# Redis connection test
@pytest.mark.asyncio
async def test_redis_client(redis_client):
    await redis_client.set("test:foo", "bar", ex=10)
    value = await redis_client.get("test:foo")
    assert value == "bar"


# Redis OTP handling tests
@pytest.mark.asyncio
async def test_redis_otp_funcs(redis_client):
    otp = otp_generator()
    email = "test@mail.com"
    key = await store_otp(redis_client, email, otp, 10)
    get_otp = await redis_client.get(key)
    check_otp = await fetch_otp(redis_client, email)

    result_1 = await verify_otp(redis_client, get_otp, check_otp, email)
    result_2 = await verify_otp(redis_client, "22030", check_otp, email)

    await delete_otp(redis_client, email)
    check_otp_after_delete = await fetch_otp(redis_client, email)
    result_3 = await verify_otp(
        redis_client,
        get_otp,
        check_otp_after_delete,
        email
    )
    print(result_3)
    assert get_otp == otp
    assert check_otp == otp
    assert result_1 is True
    assert result_2 is False
    assert check_otp_after_delete is None
    assert result_3 is False

# JWT Token tests
