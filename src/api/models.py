from pydantic import UUID4, BaseModel

from api import base_models
from shared.models import credentials as shared_credentials
from shared.models import mixins as shared_mixins
from utils.models import optional


#########################
# Project ###############
#########################
class Project(shared_mixins.ProjectMixin, BaseModel):
    id: UUID4
    owner: UUID4


class ProjectCreate(shared_mixins.ProjectMixin, base_models.BaseCreateModel):
    pass


@optional
class ProjectUpdate(shared_mixins.ProjectMixin, base_models.BaseUpdateModel):
    pass


#########################
# ProjectCredentials ####
#########################
# we do not have a regular model because we do not want to show credentials
class ProjectCredentialsCreate(
    shared_mixins.ProjectCredentialsMixin, base_models.BaseCreateModel
):
    pass


#########################
# ProjectDeploy #########
#########################
class ProjectDeployCreate(
    shared_mixins.ProjectDeployMixin, base_models.BaseCreateModel
):
    pass


#########################
# FullProjectStructure ##
#########################
class FullProjectStructure(BaseModel):
    project: Project
    credentials: shared_credentials.AWSCredentials | shared_credentials.GCPCredentials | shared_credentials.AzureCredentials
    deploy: shared_mixins.ProjectDeployMixin


#########################
# JwtUserData ###########
#########################
class JwtUserData(BaseModel):
    user_id: UUID4


class InterServiceData(BaseModel):
    user_id: UUID4
    project_id: UUID4
