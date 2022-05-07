from fastapi import Depends
from pydantic.types import UUID4

from api.models import ProjectCreate, ProjectCredentialsCreate, ProjectDeployCreate
from database.base_manager import BaseDBManager
from database.db import MongoDatabase
from database.models import (
    ProjectCredentialsDB,
    ProjectDB,
    ProjectDeployDB,
    get_project_credentials_database,
    get_project_database,
    get_project_deploy_database,
)


class ProjectManager(BaseDBManager[ProjectCreate, ProjectDB]):
    object_db_model = ProjectDB

    def create_to_db(self, create_object: ProjectCreate, user_id: UUID4) -> ProjectDB:
        return ProjectDB(**create_object.dict(), owner=user_id, created_by=user_id)

    def base_filter(self, user_id: UUID4):
        return {"owner": user_id}


class ProjectCredentialsManager(
    BaseDBManager[ProjectCredentialsCreate, ProjectCredentialsDB]
):
    object_db_model = ProjectCredentialsDB

    async def get_by_project(self, project_id: UUID4):
        result = await self.model_db.filter({"project": project_id})
        if not result:
            return None
        return result[0]


class ProjectDeployManager(BaseDBManager[ProjectDeployCreate, ProjectDeployDB]):
    object_db_model = ProjectDeployDB

    async def get_by_project(self, project_id: UUID4):
        result = await self.model_db.filter({"project": project_id})
        if not result:
            return None
        return result[0]


def get_project_manager(project_db: MongoDatabase = Depends(get_project_database)):
    return ProjectManager(project_db)


def get_project_credentials_manager(
    project_credentials_db: MongoDatabase = Depends(get_project_credentials_database),
):
    return ProjectCredentialsManager(project_credentials_db)


def get_project_deploy_manager(
    project_deploy_db: MongoDatabase = Depends(get_project_deploy_database),
):
    return ProjectDeployManager(project_deploy_db)
