from asgiref.sync import async_to_sync
from celery.utils.log import get_task_logger

from api.models import JwtUserData, ProjectDeployCreate
from database.db import DatabaseWrapper
from database.manager import get_project_deploy_manager
from database.models import (
    ProjectCredentialsDB,
    ProjectDB,
    ProjectDeployDB,
    get_project_deploy_database,
)
from shared.deployments import DEPLOYMENT_CLASSES
from worker.celery import app

LOGGER = get_task_logger(__name__)


@app.task(bind=True)
def deploy_datalake(
    self,
    jwt_user_data: dict,
    project_deploy: dict,
    project_db: dict,
    project_credentials: dict,
):
    LOGGER.info("DEPLOY")
    jwt_user_data = JwtUserData(**jwt_user_data)
    project_deploy = ProjectDeployCreate(**project_deploy)
    project_db = ProjectDB(**project_db)
    project_credentials = ProjectCredentialsDB(**project_credentials)

    deployment_class = DEPLOYMENT_CLASSES[project_deploy.deploy_type]()
    deploy_result = deployment_class.deploy_data_lake(project_db, project_credentials)
    project_deploy.project_structure = deploy_result
    project_deploy.project = project_db.id

    # TODO: rewrite this. It will cause errors because of the concurrency
    async def update_project_deploy():
        DatabaseWrapper.reset_wrapper()
        project_deploy_manager = get_project_deploy_manager(
            get_project_deploy_database()
        )
        await project_deploy_manager.create(project_deploy, jwt_user_data.user_id)

    async_to_sync(update_project_deploy)()
    LOGGER.info("DEPLOY SUCCEEDED")


@app.task(bind=True)
def destroy_datalake(
    self,
    project_deploy: dict,
    project_db: dict,
    project_credentials: dict,
):
    LOGGER.info("DESTROY")
    project_deploy = ProjectDeployDB(**project_deploy)
    project_db = ProjectDB(**project_db)
    project_credentials = ProjectCredentialsDB(**project_credentials)
    deployment_class = DEPLOYMENT_CLASSES[project_deploy.deploy_type]()
    deployment_class.delete_data_lake(project_db, project_credentials, project_deploy)

    # TODO: rewrite this. It will cause errors because of the concurrency
    async def delete_project_deploy():
        DatabaseWrapper.reset_wrapper()
        project_deploy_manager = get_project_deploy_manager(
            get_project_deploy_database()
        )
        await project_deploy_manager.delete(project_deploy)

    async_to_sync(delete_project_deploy)()
    LOGGER.info("DESTROY SUCCEEDED")
