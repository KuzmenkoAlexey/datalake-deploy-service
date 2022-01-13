import uuid

from google.cloud import bigquery
from google.oauth2 import service_account
from pydantic import BaseModel

from database.models import ProjectDB, ProjectCredentialsDB, ProjectDeployDB
from shared.deployments.base import DataLakeDeploymentInterface
from utils.gcp import get_credentials_tmp_path
from utils.logger import setup_logger

LOGGER = setup_logger()


class BigQueryResource(BaseModel):
    project: str
    dataset: str
    table: str


class GCPDeployedResources1(BaseModel):
    bigquery: BigQueryResource


class GCPDataLakeDeployment1(DataLakeDeploymentInterface):
    DATALAKE_SCHEMA = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("file", "BYTES", mode="REQUIRED"),
        bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("size", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("source", "STRING", mode="REQUIRED"),
        bigquery.SchemaField(
            "tags",
            "RECORD",
            mode="REPEATED",
            fields=[
                bigquery.SchemaField("name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("value", "STRING", mode="NULLABLE"),
            ],
        ),
    ]

    async def deploy_data_lake(
        self, project: ProjectDB, credentials: ProjectCredentialsDB
    ):
        LOGGER.info("Creating GCP Data Lake Deployment 1")
        project_id = credentials.credentials.project_id
        dataset_name = "".join(str(uuid.uuid4()).split("-"))
        table_name = "".join(str(uuid.uuid4()).split("-"))
        gcp_credentials_path = get_credentials_tmp_path(credentials.credentials)

        credentials = service_account.Credentials.from_service_account_file(
            filename=gcp_credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        client = bigquery.Client(credentials=credentials)

        LOGGER.info(f"Creating Big Query dataset {dataset_name}")
        dataset_ref = client.create_dataset(dataset_name)
        LOGGER.info(f"Big Query dataset {dataset_name} created")

        table_ref = dataset_ref.table(table_name)
        table = bigquery.Table(table_ref, schema=self.DATALAKE_SCHEMA)
        LOGGER.info(f"Creating Big Query table {table_name}")
        response = client.create_table(table)
        LOGGER.info(f"Big Query table {table_name} created: {response}")

        LOGGER.info("GCP Data Lake Deployment 1 created")
        return GCPDeployedResources1(
            bigquery={
                "project": project_id,
                "dataset": dataset_name,
                "table": table_name,
            }
        )

    async def delete_data_lake(
        self,
        project: ProjectDB,
        credentials: ProjectCredentialsDB,
        project_deploy: ProjectDeployDB,
    ):
        LOGGER.info("Deleting GCP Data Lake Deployment 1")
        deployed_resources = GCPDeployedResources1(**project_deploy.project_structure)
        gcp_credentials_path = get_credentials_tmp_path(credentials.credentials)

        credentials = service_account.Credentials.from_service_account_file(
            filename=gcp_credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        client = bigquery.Client(credentials=credentials)
        LOGGER.info(f"Creating Big Query dataset {deployed_resources.bigquery.dataset}")
        client.delete_dataset(deployed_resources.bigquery.dataset, delete_contents=True)
        LOGGER.info(f"Big Query dataset {deployed_resources.bigquery.dataset} created")
        LOGGER.info("GCP Data Lake Deployment 1 deleted")
