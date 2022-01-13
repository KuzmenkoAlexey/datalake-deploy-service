import typing
from pydantic import BaseModel, UUID4

from api import base_models
from shared import models as shared_models


#########################
# Project ###############
#########################
class Project(shared_models.ProjectMixin, BaseModel):
    id: UUID4
    owner: UUID4
    verified: bool


class ProjectCreate(shared_models.ProjectMixin, base_models.BaseCreateModel):
    pass


@shared_models.optional
class ProjectUpdate(shared_models.ProjectMixin, base_models.BaseUpdateModel):
    pass


#########################
# ProjectCredentials ####
#########################
# we do not have a regular model because we do not want to show credentials
class ProjectCredentialsCreate(
    shared_models.ProjectCredentialsMixin, base_models.BaseCreateModel
):
    pass


#########################
# ProjectDeploy #########
#########################
# we do not have a regular model because we do not want to show credentials
class ProjectDeployCreate(
    shared_models.ProjectDeployMixin, base_models.BaseCreateModel
):
    pass


class FullProjectStructure(BaseModel):
    project: Project
    credentials: typing.Union[
        shared_models.GCPCredentials, shared_models.AWSCredentials
    ]
    deploy: shared_models.ProjectDeployMixin


#########################
# JwtUserData ###########
#########################
class JwtUserData(BaseModel):
    user_id: UUID4


class InterServiceData(BaseModel):
    user_id: UUID4
    project_id: UUID4
