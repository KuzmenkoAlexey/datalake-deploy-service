from database.models import ProjectCredentialsDB, ProjectDB, ProjectDeployDB


class DataLakeDeploymentInterface:
    def deploy_data_lake(
        self, project: ProjectDB, credentials: ProjectCredentialsDB
    ) -> dict:
        raise NotImplementedError()

    def delete_data_lake(
        self,
        project: ProjectDB,
        credentials: ProjectCredentialsDB,
        project_deploy: ProjectDeployDB,
    ):
        raise NotImplementedError()
