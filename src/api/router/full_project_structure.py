from fastapi import APIRouter, Depends, status

from api.dependencies import get_current_inter_service_data
from api.models import FullProjectStructure, InterServiceData
from database.models import (
    ProjectCredentialsManager,
    ProjectDeployManager,
    ProjectManager,
    get_project_credentials_manager,
    get_project_deploy_manager,
    get_project_manager,
)

full_project_router = APIRouter(
    prefix="/v1/full_projects", tags=["full_projects"], dependencies=[]
)


@full_project_router.get(
    "", status_code=status.HTTP_200_OK, response_model=FullProjectStructure
)
async def get_full_project(
    inter_service_data: InterServiceData = Depends(get_current_inter_service_data),
    project_manager: ProjectManager = Depends(get_project_manager),
    project_deploy_manager: ProjectDeployManager = Depends(get_project_deploy_manager),
    project_credentials_manager: ProjectCredentialsManager = Depends(
        get_project_credentials_manager
    ),
) -> FullProjectStructure:
    project = await project_manager.get(
        inter_service_data.project_id, inter_service_data.user_id
    )
    project_deploy = await project_deploy_manager.get_by_project(project.id)
    if not project_deploy:
        # TODO:
        pass

    project_credentials = await project_credentials_manager.get_by_project(project.id)

    if not project_credentials:
        # TODO:
        pass

    return FullProjectStructure(
        project=project.dict(),
        credentials=project_credentials.credentials.dict(),
        deploy=project_deploy.dict(),
    )
