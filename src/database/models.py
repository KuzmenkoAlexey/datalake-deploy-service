from fastapi import Depends
from pydantic import UUID4

from api.models import ProjectCreate, ProjectCredentialsCreate, ProjectDeployCreate
from database.db import (
    BaseDBModel,
    MongoDatabase,
    get_project_collection,
    get_project_credentials_collection,
    get_project_deploy_collection,
)
from database.manager import BaseDBManager
from shared import models as shared_models


class ProjectDB(shared_models.ProjectMixin, BaseDBModel):
    owner: UUID4
    verified: bool = False


class ProjectCredentialsDB(shared_models.ProjectCredentialsMixin, BaseDBModel):
    project: UUID4


class ProjectDeployDB(shared_models.ProjectDeployMixin, BaseDBModel):
    project: UUID4
    project_structure: dict


class ProjectManager(BaseDBManager[ProjectCreate, ProjectDB]):
    object_db_model = ProjectDB

    def create_to_db(self, create_object: ProjectCreate, user_id: UUID4) -> ProjectDB:
        return ProjectDB(**create_object.dict(), owner=user_id, created_by=user_id)


class ProjectCredentialsManager(
    BaseDBManager[ProjectCredentialsCreate, ProjectCredentialsDB]
):
    object_db_model = ProjectCredentialsDB

    def create_to_db(
        self, create_object: ProjectCredentialsCreate, user_id: UUID4
    ) -> ProjectCredentialsDB:
        return ProjectCredentialsDB(**create_object.dict(), created_by=user_id)

    def base_filter(self, user_id: UUID4):
        return {"created_by": user_id}

    async def get_by_project(self, project_id: UUID4):
        result = await self.model_db.filter({"project": project_id})
        if not result:
            return None
        return result[0]


class ProjectDeployManager(BaseDBManager[ProjectDeployCreate, ProjectDeployDB]):
    object_db_model = ProjectDeployDB

    def create_to_db(
        self, create_object: ProjectDeployCreate, user_id: UUID4
    ) -> ProjectDeployDB:
        return ProjectDeployDB(**create_object.dict(), created_by=user_id)

    def base_filter(self, user_id: UUID4):
        return {"created_by": user_id}

    async def get_by_project(self, project_id: UUID4):
        result = await self.model_db.filter({"project": project_id})
        if not result:
            return None
        return result[0]


def get_project_database() -> MongoDatabase:
    return MongoDatabase(ProjectDB, get_project_collection())


def get_project_credentials_database() -> MongoDatabase:
    return MongoDatabase(ProjectCredentialsDB, get_project_credentials_collection())


def get_project_deploy_database() -> MongoDatabase:
    return MongoDatabase(ProjectDeployDB, get_project_deploy_collection())


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
