import uuid

from boto3 import client
from botocore.client import Config
from pydantic import BaseModel

from database.models import ProjectCredentialsDB, ProjectDB, ProjectDeployDB
from shared.deployments.base import DataLakeDeploymentInterface
from utils.logger import setup_logger

LOGGER = setup_logger()


class S3DeployedResource(BaseModel):
    bucket_name: str


class OpenSearchResource(BaseModel):
    domain_name: str


class AWSDeployedResources1(BaseModel):
    s3: S3DeployedResource
    opensearch: OpenSearchResource


class AWSDataLakeDeployment1(DataLakeDeploymentInterface):
    async def deploy_data_lake(
        self, project: ProjectDB, credentials: ProjectCredentialsDB
    ):
        LOGGER.info("Creating AWS Data Lake Deployment 1")
        kwargs = {
            "aws_access_key_id": credentials.credentials.access_key_id,
            "aws_secret_access_key": credentials.credentials.secret_access_key,
            # TODO:
            "config": Config(region_name="us-east-1"),
        }
        s3_client = client("s3", **kwargs)
        os_client = client("opensearch", **kwargs)

        bucket_name = f"{uuid.uuid4()}-{project.id}"[:63]
        LOGGER.info(f"Creating S3 bucket with name {bucket_name}")
        response = s3_client.create_bucket(Bucket=bucket_name)
        LOGGER.info(f"Bucket created, response: {response}")

        domain_name = (
            f"osdomain{''.join(str(uuid.uuid4()).split('-'))}"
            f"{''.join(str(project.id).split('-'))}"[:28]
        )
        LOGGER.info(f"Creating OpenSearch with Domain Name {domain_name}")
        response = os_client.create_domain(
            DomainName=domain_name,
            EngineVersion="OpenSearch_1.0",
            ClusterConfig={
                "InstanceType": "t2.small.search",
                "InstanceCount": 3,
            },
            # Many instance types require EBS storage.
            EBSOptions={"EBSEnabled": True, "VolumeType": "gp2", "VolumeSize": 10},
        )

        LOGGER.info(f"OpenSearch created, response: {response}")
        LOGGER.info("AWS Data Lake Deployment 1 created")

        return AWSDeployedResources1(
            s3={"bucket_name": bucket_name},
            opensearch={"domain_name": domain_name},
        )

    async def delete_data_lake(
        self,
        project: ProjectDB,
        credentials: ProjectCredentialsDB,
        project_deploy: ProjectDeployDB,
    ):
        LOGGER.info("Deleting AWS Data Lake Deployment 1")
        deployed_resources = AWSDeployedResources1(**project_deploy.project_structure)
        kwargs = {
            "aws_access_key_id": credentials.credentials.access_key_id,
            "aws_secret_access_key": credentials.credentials.secret_access_key,
            # TODO:
            "config": Config(region_name="us-east-1"),
        }
        s3_client = client("s3", **kwargs)
        os_client = client("opensearch", **kwargs)
        LOGGER.info(f"Deleting S3 bucket with name {deployed_resources.s3.bucket_name}")
        response = s3_client.delete_bucket(Bucket=deployed_resources.s3.bucket_name)
        LOGGER.info(f"Bucket created, response: {response}")

        LOGGER.info(
            f"Deleting OpenSearch with Domain Name "
            f"{deployed_resources.opensearch.domain_name}"
        )
        response = os_client.delete_domain(
            DomainName=deployed_resources.opensearch.domain_name
        )
        LOGGER.info(f"OpenSearch deleted, response: {response}")
        LOGGER.info("AWS Data Lake Deployment 1 deleted")
