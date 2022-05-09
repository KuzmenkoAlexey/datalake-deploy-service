import os
import subprocess
import uuid

from pydantic import BaseModel

from database.models import ProjectCredentialsDB, ProjectDB, ProjectDeployDB
from shared.deployments.base import DataLakeDeploymentInterface
from utils.logger import setup_logger

LOGGER = setup_logger()


class S3DeployedResource(BaseModel):
    bucket_name: str


class DynamoDBResource(BaseModel):
    dynamodb_name: str


class AWSDeployedResources2(BaseModel):
    s3: S3DeployedResource
    dynamodb: DynamoDBResource


TF_STATE = """
terraform {{
  backend "gcs" {{
    bucket  = "qqbucket"
    prefix  = "terraform/{}"
  }}
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }}
  }}
}}

# Configure the AWS Provider
provider "aws" {{
  region = "us-east-1"
}}

"""

AWS_STORAGE = """
resource "aws_s3_bucket" "b" {{
  bucket = "{}"
}}
"""


AWS_DYNAMODB = """
resource "aws_dynamodb_table" "basic-dynamodb-table" {{
  name           = "{}"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1
  write_capacity = 1
  hash_key       = "id"

  attribute {{
    name = "id"
    type = "S"
  }}
}}
"""


class AWSDataLakeDeployment2(DataLakeDeploymentInterface):
    def deploy_data_lake(self, project: ProjectDB, credentials: ProjectCredentialsDB):
        LOGGER.info("Creating AWS Data Lake Deployment 2")
        this_env = dict(
            os.environ,
            AWS_ACCESS_KEY_ID=credentials.credentials.access_key_id,
            AWS_SECRET_ACCESS_KEY=credentials.credentials.secret_access_key,
        )

        directory_path = f"/usr/app/infrastructure/{project.id}"
        os.makedirs(directory_path, exist_ok=True)
        with open(os.path.join(directory_path, "state.tf"), "w") as f:
            tf_state_f = TF_STATE.format(str(project.id))
            f.write(tf_state_f)

        process = subprocess.run(
            ["terraform", f"-chdir={directory_path}", "init"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=this_env,
        )
        LOGGER.debug(
            f"Terraform init execution result:\n"
            f"stdout: '{process.stdout.decode()}'\n"
            f"stderr:{process.stderr.decode()}\n"
            f"exit code:{process.returncode}"
        )

        bucket_name = f"{uuid.uuid4()}-{project.id}"[:63]
        dynamodb_name = f"{uuid.uuid4()}-{project.id}"[:63]

        LOGGER.info(f"Creating S3 bucket with name {bucket_name}")
        with open(os.path.join(directory_path, "bucket.tf"), "w") as f:
            f.write(AWS_STORAGE.format(bucket_name))

        domain_name = (
            f"osdomain{''.join(str(uuid.uuid4()).split('-'))}"
            f"{''.join(str(project.id).split('-'))}"[:28]
        )
        LOGGER.info(f"Creating DynamoDB with name {dynamodb_name}")
        with open(os.path.join(directory_path, "es.tf"), "w") as f:
            f.write(AWS_DYNAMODB.format(domain_name))

        process = subprocess.run(
            ["terraform", f"-chdir={directory_path}", "apply", "-auto-approve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=this_env,
        )
        LOGGER.debug(
            f"Terraform apply execution result:\n"
            f"stdout: '{process.stdout.decode()}'\n"
            f"stderr:{process.stderr.decode()}\n"
            f"exit code:{process.returncode}"
        )
        LOGGER.info("AWS Data Lake Deployment 2 created")
        return AWSDeployedResources2(
            s3={"bucket_name": bucket_name},
            dynamodb={"dynamodb_name": dynamodb_name},
        )

    def delete_data_lake(
        self,
        project: ProjectDB,
        credentials: ProjectCredentialsDB,
        project_deploy: ProjectDeployDB,
    ):
        LOGGER.info("Deleting AWS Data Lake Deployment 2")
        this_env = dict(
            os.environ,
            AWS_ACCESS_KEY_ID=credentials.credentials.access_key_id,
            AWS_SECRET_ACCESS_KEY=credentials.credentials.secret_access_key,
        )
        directory_path = f"/usr/app/infrastructure/{project.id}"
        process = subprocess.run(
            ["terraform", f"-chdir={directory_path}", "destroy", "-auto-approve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=this_env,
        )
        LOGGER.debug(
            f"Terraform destroy execution result:\n"
            f"stdout: '{process.stdout.decode()}'\n"
            f"stderr:{process.stderr.decode()}\n"
            f"exit code:{process.returncode}"
        )
        LOGGER.info("AWS Data Lake Deployment 2 deleted")
