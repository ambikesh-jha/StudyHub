from __future__ import annotations

import pytest

from tests.factories import AuthPayloadFactory


@pytest.mark.asyncio
async def test_auth_flow(client):
    payload = AuthPayloadFactory()

    register_response = await client.post("/api/v1/register", json=payload)
    assert register_response.status_code == 201
    register_body = register_response.json()
    assert register_body["user"]["email"] == payload["email"]

    login_response = await client.post("/api/v1/login", json={"email": payload["email"], "password": payload["password"]})
    assert login_response.status_code == 200
    login_body = login_response.json()
    assert login_body["tokens"]["access_token"]

    refresh_response = await client.post("/api/v1/refresh", json={"refresh_token": login_body["tokens"]["refresh_token"]})
    assert refresh_response.status_code == 200
    refresh_body = refresh_response.json()
    assert refresh_body["tokens"]["access_token"]

    logout_response = await client.post("/api/v1/logout", json={"refresh_token": refresh_body["tokens"]["refresh_token"]})
    assert logout_response.status_code == 200


@pytest.mark.asyncio
async def test_private_courses_are_user_scoped(client):
    owner_payload = AuthPayloadFactory()
    other_payload = AuthPayloadFactory()
    owner_response = await client.post("/api/v1/register", json=owner_payload)
    other_response = await client.post("/api/v1/register", json=other_payload)
    owner_headers = {"Authorization": f"Bearer {owner_response.json()['tokens']['access_token']}"}
    other_headers = {"Authorization": f"Bearer {other_response.json()['tokens']['access_token']}"}

    course_response = await client.post(
        "/api/v1/courses",
        json={"title": "Private Course", "description": None, "icon": "book", "color": "purple", "is_published": False},
        headers=owner_headers,
    )
    assert course_response.status_code == 201
    course_id = course_response.json()["id"]

    other_list = await client.get("/api/v1/courses", headers=other_headers)
    assert other_list.status_code == 200
    assert all(item["id"] != course_id for item in other_list.json()["items"])

    other_get = await client.get(f"/api/v1/courses/{course_id}", headers=other_headers)
    assert other_get.status_code == 401
