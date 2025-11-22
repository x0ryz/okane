import pytest
import asyncio

USER_EMAIL = "test_refresh@example.com"
USER_PASSWORD = "password123"


@pytest.mark.asyncio
async def test_refresh_token_flow(client):
    reg_resp = await client.post("/auth/register", json={"email": USER_EMAIL, "password": USER_PASSWORD})
    assert reg_resp.status_code == 200
    old_access_token = reg_resp.json()["access_token"]

    await asyncio.sleep(1.1)

    refresh_resp = await client.post("/auth/refresh")

    assert refresh_resp.status_code == 200
    new_data = refresh_resp.json()
    assert new_data["access_token"] != old_access_token