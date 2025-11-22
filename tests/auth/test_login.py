import pytest

USER_EMAIL = "test_login@example.com"
USER_PASSWORD = "password123"

@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/auth/register", json={"email": USER_EMAIL, "password": USER_PASSWORD})

    response = await client.post("/auth/login", json={
        "email": USER_EMAIL,
        "password": USER_PASSWORD
    })

    assert response.status_code == 200
    assert response.json()["user"]["email"] == USER_EMAIL
    assert "user_refresh_token" in client.cookies

@pytest.mark.asyncio
async def test_login_invalid_credentials(client):
    await client.post("/auth/register", json={"email": USER_EMAIL, "password": USER_PASSWORD})

    response = await client.post("/auth/login", json={
        "email": USER_EMAIL,
        "password": "wrongpassword"
    })

    assert response.status_code == 401