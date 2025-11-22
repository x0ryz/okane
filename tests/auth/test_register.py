import pytest

USER_EMAIL = "test_reg@example.com"
USER_PASSWORD = "password123"

@pytest.mark.asyncio
async def test_register_web_flow(client):
    response = await client.post("/auth/register", json={
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    })

    assert response.status_code == 200
    data = response.json()
    assert data["refresh_token"] is None
    assert "user_refresh_token" in client.cookies

@pytest.mark.asyncio
async def test_register_mobile_flow(client):
    response = await client.post(
        "/auth/register",
        json={"email": "mobile@example.com", "password": USER_PASSWORD},
        headers={"x-client-type": "mobile"}
    )

    assert response.status_code == 200
    assert response.json()["refresh_token"] is not None