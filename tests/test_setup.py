import pytest
import asyncio
from fastapi import HTTPException
from datetime import timedelta
from backend.services.otp import otp_generator
from backend.services.redis_otp import (
    store_otp,
    delete_otp,
    fetch_otp,
    verify_otp
)
from backend.services.jwt_token import (
    create_access_token,
    create_refresh_token,
    create_otp_token,
    refresh_access_token,
    create_token,
    decode_token,
    token_type,
)


# 1. Basic app health tests
def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# 2. Basic app api tests
def test_hello(client):
    response = client.get("/hello?name=Maude")
    assert response.status_code == 200
    assert response.json()["greeting"] == "Hello, Maude!"


# 3. OTP generation tests
def test_otp_generation():
    otp = otp_generator()
    assert type(otp) is str
    assert len(otp) == 8


# 4. Redis connection tests
@pytest.mark.asyncio
async def test_redis_client(redis_client):
    await redis_client.set("test:foo", "bar", ex=10)
    value = await redis_client.get("test:foo")
    assert value == "bar"


# 5. Redis OTP handling tests
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


# 6. JWT OTP Token tests
@pytest.mark.asyncio
async def test_otp_token(redis_client):
    email = "jwt_otp@mail.com"
    otp_payload = {
            "sub": email,
        }
    otp_token = await create_otp_token(redis_client, otp_payload)
    print(otp_token)
    decode_payload = decode_token(otp_token)

    assert type(otp_token) is str
    assert type(decode_payload) is dict
    assert token_type(decode_payload, "otp") is True
    assert decode_payload.get("sub") == email


# 7. JWT access/ refresh Token tests
@pytest.mark.asyncio
async def test_login_token(redis_client):
    access_payload = {
        "sub": "1000",
    }
    access_token = await create_access_token(redis_client, access_payload)
    refresh_payload = {
        "sub": "1000",
    }
    refresh_token = await create_refresh_token(redis_client, refresh_payload)

    decode_access = decode_token(access_token)
    decode_refresh = decode_token(refresh_token)

    assert type(access_token) is str
    assert type(refresh_token) is str
    assert type(decode_access) is dict
    assert token_type(decode_access, "access") is True
    assert token_type(decode_access, "refresh") is False
    assert type(decode_refresh) is dict
    assert token_type(decode_refresh, "access") is False
    assert token_type(decode_refresh, "refresh") is True
    assert decode_access.get("sub") == "1000"
    assert decode_refresh.get("sub") == "1000"
    assert decode_access.get("sub") != "100"
    assert decode_refresh.get("sub") != "100"


# 8. Test refresh access token tests
@pytest.mark.asyncio
async def test_token_expire(redis_client):

    access_payload = {
        "sub": "2000",
    }
    access_token, jti_a = create_token(
        access_payload,
        "access",
        timedelta(seconds=-1)  # Expire immediately
    )
    refresh_payload = {
        "sub": "2000",
    }
    refresh_token, jti_r = create_token(
        refresh_payload,
        "refresh",
        timedelta(seconds=60)
    )
    user_id = refresh_payload["sub"]
    key = f"jti:refresh:{user_id}:{jti_r}"
    await redis_client.setex(key, 60, "valid")

    decode_access = decode_token(access_token)
    decode_refresh = decode_token(refresh_token)

    assert decode_access == "expired"
    assert type(refresh_token) is str
    assert type(decode_refresh) is dict
    assert token_type(decode_refresh, "access") is False
    assert token_type(decode_refresh, "refresh") is True
    assert decode_refresh.get("sub") == "2000"

    redis_value = await redis_client.get(key)
    assert redis_value == "valid", f"Unexpected Redis value: {redis_value}"

    true_new_access = await refresh_access_token(redis_client, refresh_token)
    decode_new_payload = decode_token(true_new_access)

    assert type(true_new_access) is str
    assert type(decode_new_payload) is dict
    assert token_type(decode_new_payload, "access") is True
    assert token_type(decode_new_payload, "refresh") is False
    assert decode_new_payload.get("sub") == "2000"
    assert decode_new_payload.get("sub") != "1000"

######### wrong refresh token
    wrong_refresh_token, jti_w = create_token(
        refresh_payload,
        "wrong",
        timedelta(seconds=10)
    )
    user_id_w = refresh_payload["sub"]
    key_w = f"jti:refresh:{user_id_w}:{jti_w}"
    await redis_client.setex(key_w, 10, "valid")

    with pytest.raises(HTTPException) as exc_info:
        await refresh_access_token(redis_client, wrong_refresh_token)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid refresh token."

######### expired refresh token
    exp_refresh_token, jti_x = create_token(
        refresh_payload,
        "refresh",
        timedelta(seconds=-1)
    )
    user_id_x = refresh_payload["sub"]
    key_x = f"jti:refresh:{user_id_x}:{jti_x}"
    await redis_client.setex(key_x, 1, "valid")
    await asyncio.sleep(1.1)

    with pytest.raises(HTTPException) as exc_info_2:
        await refresh_access_token(redis_client, exp_refresh_token)

    assert exc_info_2.value.status_code == 401
    assert exc_info_2.value.detail == "Token expired."
