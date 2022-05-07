from fastapi import APIRouter, Depends, status

from api.dependencies import get_current_user, get_project_or_404
from api.models import JwtUserData, Project, ProjectCreate, ProjectUpdate
from database.manager import ProjectManager, get_project_manager
from database.models import ProjectDB

projects_router = APIRouter(prefix="/v1/projects", tags=["projects"], dependencies=[])


@projects_router.post("", status_code=status.HTTP_201_CREATED, response_model=Project)
async def create_project(
    project: ProjectCreate,
    jwt_user_data: JwtUserData = Depends(get_current_user),
    project_manager: ProjectManager = Depends(get_project_manager),
) -> Project:
    project_db = await project_manager.create(project, jwt_user_data.user_id)

    return Project(**project_db.dict())


@projects_router.get(
    "/{project_id}", status_code=status.HTTP_200_OK, response_model=Project
)
async def get_project(project_db: ProjectDB = Depends(get_project_or_404)) -> Project:
    return Project(**project_db.dict())


@projects_router.get("/", status_code=status.HTTP_200_OK, response_model=list[Project])
async def list_projects(
    jwt_user_data: JwtUserData = Depends(get_current_user),
    project_manager: ProjectManager = Depends(get_project_manager),
) -> list[Project]:
    results = await project_manager.list(jwt_user_data.user_id)
    return [Project(**res.dict()) for res in results]


@projects_router.patch(
    "/{project_id}", status_code=status.HTTP_200_OK, response_model=Project
)
async def update_project(
    project: ProjectUpdate,
    project_db: ProjectDB = Depends(get_project_or_404),
    jwt_user_data: JwtUserData = Depends(get_current_user),
    project_manager: ProjectManager = Depends(get_project_manager),
):
    updated_object = await project_manager.update(
        project, project_db, jwt_user_data.user_id
    )
    return Project(**updated_object.dict())


@projects_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_db: ProjectDB = Depends(get_project_or_404),
    project_manager: ProjectManager = Depends(get_project_manager),
):
    await project_manager.delete(project_db)
    return None
