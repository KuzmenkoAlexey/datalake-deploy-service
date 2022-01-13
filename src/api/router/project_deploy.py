from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse, Response

from api.dependencies import get_current_user, get_project_or_404
from api.models import ProjectDeployCreate, JwtUserData
from database.models import (
    get_project_deploy_manager,
    get_project_manager,
    get_project_credentials_manager,
    ProjectDeployManager,
    ProjectManager,
    ProjectDB,
    ProjectCredentialsManager,
)
from shared.deployments import DEPLOYMENT_CLASSES

project_deploy_router = APIRouter(
    prefix="/v1/project_deploy", tags=["deploy"], dependencies=[]
)


@project_deploy_router.post("/{project_id}", status_code=status.HTTP_201_CREATED)
async def create_project_deploy(
    project_deploy: ProjectDeployCreate,
    project_db: ProjectDB = Depends(get_project_or_404),
    jwt_user_data: JwtUserData = Depends(get_current_user),
    project_deploy_manager: ProjectDeployManager = Depends(get_project_deploy_manager),
    project_credentials_manager: ProjectCredentialsManager = Depends(
        get_project_credentials_manager
    ),
    project_manager: ProjectManager = Depends(get_project_manager),
) -> JSONResponse:
    if not project_db.verified:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "project doesn't have valid credentials"},
        )

    another_pd = await project_deploy_manager.get_by_project(project_db.id)
    if another_pd:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "project already deployed"},
        )

    project_credentials = await project_credentials_manager.get_by_project(
        project_db.id
    )

    if not project_credentials:
        # TODO:
        pass

    deployment_class = DEPLOYMENT_CLASSES[project_deploy.deploy_type]()
    deploy_result = await deployment_class.deploy_data_lake(
        project_db, project_credentials
    )

    project_deploy.project = project_db.id
    project_deploy.project_structure = deploy_result
    await project_deploy_manager.create(project_deploy, jwt_user_data.user_id)

    return JSONResponse(status_code=status.HTTP_201_CREATED)


@project_deploy_router.delete("/{project_id}")
async def delete_project_deploy(
    project_db: ProjectDB = Depends(get_project_or_404),
    jwt_user_data: JwtUserData = Depends(get_current_user),
    project_deploy_manager: ProjectDeployManager = Depends(get_project_deploy_manager),
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

    project_deploy = await project_deploy_manager.get_by_project(project_db.id)
    if not project_deploy:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "project not deployed"},
        )

    project_credentials = await project_credentials_manager.get_by_project(
        project_db.id
    )

    if not project_credentials:
        # TODO:
        pass

    deployment_class = DEPLOYMENT_CLASSES[project_deploy.deploy_type]()
    await deployment_class.delete_data_lake(
        project_db, project_credentials, project_deploy
    )

    await project_deploy_manager.delete(project_deploy)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
