from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response

from api.credential_verifiers import verify_credentials
from api.dependencies import get_current_user, get_project_or_404
from api.models import JwtUserData, ProjectCredentialsCreate, ProjectUpdate
from database.manager import (
    ProjectCredentialsManager,
    ProjectManager,
    get_project_credentials_manager,
    get_project_manager,
)
from database.models import ProjectDB

project_credentials_router = APIRouter(
    prefix="/v1/project_credentials", tags=["credentials"], dependencies=[]
)


@project_credentials_router.post("/{project_id}", status_code=status.HTTP_201_CREATED)
async def create_project_credentials(
    project_credentials: ProjectCredentialsCreate,
    project_db: ProjectDB = Depends(get_project_or_404),
    jwt_user_data: JwtUserData = Depends(get_current_user),
    project_credentials_manager: ProjectCredentialsManager = Depends(
        get_project_credentials_manager
    ),
    project_manager: ProjectManager = Depends(get_project_manager),
) -> JSONResponse:
    if project_db.verified:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "project already has valid credentials"},
        )

    verified = await verify_credentials(project_db, project_credentials)
    if not verified:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "invalid credentials"},
        )

    project_credentials.project = project_db.id
    await project_credentials_manager.create(project_credentials, jwt_user_data.user_id)
    await project_manager.update(
        ProjectUpdate(verified=True), project_db, jwt_user_data.user_id, safe=False
    )

    return JSONResponse(status_code=status.HTTP_201_CREATED)


@project_credentials_router.delete("/{project_id}")
async def delete_project(
    project_db: ProjectDB = Depends(get_project_or_404),
    jwt_user_data: JwtUserData = Depends(get_current_user),
    project_credentials_manager: ProjectCredentialsManager = Depends(
        get_project_credentials_manager
    ),
    project_manager: ProjectManager = Depends(get_project_manager),
):
    if not project_db.verified:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "project does not have credentials"},
        )
    project_credentials = await project_credentials_manager.list(
        jwt_user_data.user_id, project=project_db.id
    )
    # in case something went wrong
    for pc in project_credentials:
        await project_credentials_manager.delete(pc)

    await project_manager.update(
        ProjectUpdate(verified=False), project_db, jwt_user_data.user_id, safe=False
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
