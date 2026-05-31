from __future__ import annotations

import pytest

from tests.factories import AuthPayloadFactory, ProfilePayloadFactory


@pytest.mark.asyncio
async def test_profile_update(client):
    payload = AuthPayloadFactory()
    register_response = await client.post("/api/v1/register", json=payload)
    tokens = register_response.json()["tokens"]

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    profile_payload = ProfilePayloadFactory()
    update_response = await client.patch("/api/v1/users/me", json=profile_payload, headers=headers)
    assert update_response.status_code == 200
    update_body = update_response.json()
    assert update_body["display_name"] == profile_payload["display_name"]
    assert update_body["bio"] == profile_payload["bio"]

    me_response = await client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == profile_payload["email"]

