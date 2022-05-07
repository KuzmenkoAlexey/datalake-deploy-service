from pydantic import UUID4, BaseModel

from shared.models.credentials import AWSCredentials, AzureCredentials, GCPCredentials
from shared.models.deploy_types import (
    AWSProjectDeployType,
    AzureProjectDeployType,
    GCPProjectDeployType,
)
from shared.models.providers import ServiceProviderType


class ProjectMixin(BaseModel):
    verified: bool = False
    name: str
    service_provider: ServiceProviderType

    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "verified",
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class ProjectCredentialsMixin(BaseModel):
    project: UUID4 | None
    credentials: GCPCredentials | AWSCredentials | AzureCredentials

    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "project",
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})


class ProjectDeployMixin(BaseModel):
    project: UUID4 | None
    deploy_type: AWSProjectDeployType | GCPProjectDeployType | AzureProjectDeployType
    project_structure: dict | None

    def create_update_dict(self):
        return self.dict(
            exclude_unset=True,
            exclude={
                "id",
                "project",
            },
        )

    def create_update_dict_superuser(self):
        return self.dict(exclude_unset=True, exclude={"id"})
