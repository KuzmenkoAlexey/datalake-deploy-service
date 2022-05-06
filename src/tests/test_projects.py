from uuid import uuid4

import httpx
import jwt
import pytest
from faker import Faker

from api.app import get_application
from config import settings

fake = Faker()
JWT_ALGORITHM = "HS256"


@pytest.mark.asyncio
async def test_create_project_unathenticated(event_loop):
    app = get_application(event_loop)
    async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.post("/v1/projects", json={"name": "test"})
        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}


@pytest.mark.asyncio
async def test_get_projects_unathenticated(event_loop):
    app = get_application(event_loop)
    async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get("/v1/projects/")
        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}


@pytest.mark.asyncio
async def test_get_project_unathenticated(event_loop):
    app = get_application(event_loop)
    random_project_id = str(uuid4())
    async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
        response = await async_client.get(f"/v1/projects/{random_project_id}")
        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}


@pytest.mark.asyncio
async def test_create_projects_valid(event_loop):
    app = get_application(event_loop)
    user_id = str(uuid4())
    access_token = jwt.encode(
        {"user_id": user_id, "aud": ["fastapi-users:auth"]},
        settings.jwt_secret,
        algorithm=JWT_ALGORITHM,
    )
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
        created_projects = []
        for post_data in [
            {"name": "test gcp project", "service_provider": "GCP"},
            {"name": "test aws project", "service_provider": "AWS"},
            {"name": "test azure project", "service_provider": "AZURE"},
        ]:
            response = await async_client.post(
                "/v1/projects", json=post_data, headers=auth_headers
            )
            assert response.status_code == 201, response.content
            response_json = response.json()
            project_id = response_json.pop("id")
            expected_data = {"owner": user_id, "verified": False, **post_data}
            assert response_json == expected_data
            expected_data["id"] = project_id
            created_projects.append(expected_data)

        response = await async_client.get("/v1/projects/", headers=auth_headers)
        assert response.status_code == 200, response.content
        response_json = response.json()
        assert response_json == created_projects

        response = await async_client.delete(
            f"/v1/projects/{created_projects[0]['id']}", headers=auth_headers
        )
        assert response.status_code == 204, response.content
        response_json = response.json()
        assert response_json is None

        created_projects.pop(0)
        response = await async_client.get("/v1/projects/", headers=auth_headers)
        assert response.status_code == 200, response.content
        response_json = response.json()
        assert response_json == created_projects

        for proj in created_projects:
            response = await async_client.delete(
                f"/v1/projects/{proj['id']}", headers=auth_headers
            )
            assert response.status_code == 204, response.content
            response_json = response.json()
            assert response_json is None

        response = await async_client.get("/v1/projects/", headers=auth_headers)
        assert response.status_code == 200, response.content
        response_json = response.json()
        assert response_json == []
