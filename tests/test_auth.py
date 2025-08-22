import pytest
import asyncio
from fastapi import HTTPException
from backend.routers.auth import (
    create_user,
    login,
    verify_user,
    logout,
    refresh_token,
    get_current_user,
)


def test_login_success(client, db_session):
    pass
