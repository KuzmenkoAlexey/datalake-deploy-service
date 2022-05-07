from pydantic import UUID4

from database.base_models import BaseDBModel
from database.db import (
    MongoDatabase,
    get_project_collection,
    get_project_credentials_collection,
    get_project_deploy_collection,
)
from shared.models import mixins as shared_mixins


class ProjectDB(shared_mixins.ProjectMixin, BaseDBModel):
    owner: UUID4
    verified: bool = False


class ProjectCredentialsDB(shared_mixins.ProjectCredentialsMixin, BaseDBModel):
    project: UUID4


class ProjectDeployDB(shared_mixins.ProjectDeployMixin, BaseDBModel):
    project: UUID4
    project_structure: dict


def get_project_database() -> MongoDatabase:
    return MongoDatabase(ProjectDB, get_project_collection())


def get_project_credentials_database() -> MongoDatabase:
    return MongoDatabase(ProjectCredentialsDB, get_project_credentials_collection())


def get_project_deploy_database() -> MongoDatabase:
    return MongoDatabase(ProjectDeployDB, get_project_deploy_collection())
