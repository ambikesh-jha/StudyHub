from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.models.course import ShareLink
from tests.factories import AuthPayloadFactory, CoursePayloadFactory


@pytest.mark.asyncio
async def test_share_link_generation_and_expiry(client, session):
    payload = AuthPayloadFactory()
    register_response = await client.post("/api/v1/register", json=payload)
    tokens = register_response.json()["tokens"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    course_payload = CoursePayloadFactory()
    course_response = await client.post("/api/v1/courses", json=course_payload, headers=headers)
    assert course_response.status_code == 201
    course_id = course_response.json()["id"]

    topic_response = await client.post(
        f"/api/v1/courses/{course_id}/topics",
        json={"title": "Getting started", "position": 0, "status": "todo"},
        headers=headers,
    )
    assert topic_response.status_code == 201

    share_response = await client.get(f"/api/v1/courses/{course_id}/share-link", headers=headers)
    assert share_response.status_code == 200
    share_body = share_response.json()
    assert share_body["token"]

    preview_response = await client.get(f"/api/v1/shared/course/{share_body['token']}")
    assert preview_response.status_code == 200
    preview_body = preview_response.json()
    assert preview_body["course"]["id"] == course_id

    analytics_response = await client.get(f"/api/v1/courses/{course_id}/share-links", headers=headers)
    assert analytics_response.status_code == 200
    analytics_body = analytics_response.json()
    assert analytics_body["total_access_count"] == 1
    assert analytics_body["items"][0]["access_count"] == 1

    result = await session.execute(select(ShareLink).where(ShareLink.token == share_body["token"]))
    share_link = result.scalar_one()
    share_link.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    await session.commit()

    expired_response = await client.get(f"/api/v1/shared/course/{share_body['token']}")
    assert expired_response.status_code == 410
