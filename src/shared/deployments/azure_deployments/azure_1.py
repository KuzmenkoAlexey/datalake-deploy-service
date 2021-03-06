from database.models import ProjectCredentialsDB, ProjectDB, ProjectDeployDB
from shared.deployments.base import DataLakeDeploymentInterface
from utils.logger import setup_logger

LOGGER = setup_logger()


class AzureDataLakeDeployment1(DataLakeDeploymentInterface):
    def deploy_data_lake(self, project: ProjectDB, credentials: ProjectCredentialsDB):
        # TODO:
        return {}

    def delete_data_lake(
        self,
        project: ProjectDB,
        credentials: ProjectCredentialsDB,
        project_deploy: ProjectDeployDB,
    ):
        # TODO:
        pass
