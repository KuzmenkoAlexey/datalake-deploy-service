import time
import uuid

from google.cloud import bigtable, storage
from google.cloud.bigtable.enums import StorageType
from google.oauth2 import service_account
from pydantic import BaseModel

from database.models import ProjectDB, ProjectCredentialsDB, ProjectDeployDB
from shared.deployments.base import DataLakeDeploymentInterface
from utils.gcp import get_credentials_tmp_path
from utils.logger import setup_logger

LOGGER = setup_logger()


class BigTableResource(BaseModel):
    project: str
    instance: str
    table: str


class CloudStorage(BaseModel):
    bucket: str


class GCPDeployedResources2(BaseModel):
    bigtable: BigTableResource
    cloud_storage: CloudStorage


class GCPDataLakeDeployment2(DataLakeDeploymentInterface):
    async def deploy_data_lake(
        self, project: ProjectDB, credentials: ProjectCredentialsDB
    ):
        # TODO: rewrite in async
        LOGGER.info("Creating GCP Data Lake Deployment 2")
        project_id = credentials.credentials.project_id
        gcp_credentials_path = get_credentials_tmp_path(credentials.credentials)

        credentials = service_account.Credentials.from_service_account_file(
            filename=gcp_credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        bigtable_client = bigtable.Client(credentials=credentials, admin=True)
        storage_client = storage.Client(credentials=credentials)

        instance_id = "in" + "".join(str(uuid.uuid4()).split("-"))[:10]
        table_id = "table" + "".join(str(uuid.uuid4()).split("-"))[:10]
        bucket_name = "bucket" + "".join(str(uuid.uuid4()).split("-"))[:10]

        inst = bigtable_client.instance(instance_id)
        inst.create(
            location_id="us-central1-a",
            serve_nodes=1,
            default_storage_type=StorageType.HDD,
        )
        while not inst.exists() or not inst.list_clusters():
            LOGGER.info("Not exists")
            time.sleep(1)
        table = inst.table(table_id)
        table.create()

        storage_client.create_bucket(bucket_name)

        # TODO: review Column Families
        cf_name = "ColumnFamily"
        cf = table.column_family(cf_name)
        cf.create()

        LOGGER.info("GCP Data Lake Deployment 2 created")
        return GCPDeployedResources2(
            bigtable={
                "project": project_id,
                "instance": inst.instance_id,
                "table": table_id,
            },
            cloud_storage={"bucket": bucket_name},
        )

    async def delete_data_lake(
        self,
        project: ProjectDB,
        credentials: ProjectCredentialsDB,
        project_deploy: ProjectDeployDB,
    ):
        # TODO: rewrite in async
        LOGGER.info("Deleting GCP Data Lake Deployment 2")
        deployed_resources = GCPDeployedResources2(**project_deploy.project_structure)
        gcp_credentials_path = get_credentials_tmp_path(credentials.credentials)

        credentials = service_account.Credentials.from_service_account_file(
            filename=gcp_credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

        bigtable_client = bigtable.Client(credentials=credentials, admin=True)
        storage_client = storage.Client(credentials=credentials)

        inst = bigtable_client.instance(deployed_resources.bigtable.instance)
        inst.delete()

        bucket = storage_client.bucket(deployed_resources.cloud_storage.bucket)
        bucket.delete(force=True)

        LOGGER.info("GCP Data Lake Deployment 2 deleted")
