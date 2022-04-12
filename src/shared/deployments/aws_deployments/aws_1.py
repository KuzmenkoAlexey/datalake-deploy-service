import os
import re
import subprocess
import uuid

from pydantic import BaseModel

from database.models import ProjectCredentialsDB, ProjectDB, ProjectDeployDB
from shared.deployments.base import DataLakeDeploymentInterface
from utils.logger import setup_logger

LOGGER = setup_logger()


class S3DeployedResource(BaseModel):
    bucket_name: str


class OpenSearchResource(BaseModel):
    domain_name: str
    endpoint: str


class AWSDeployedResources1(BaseModel):
    s3: S3DeployedResource
    opensearch: OpenSearchResource


TF_STATE = """
terraform {{
  backend "gcs" {{
    bucket  = "insmouth-lake-dev-proj-tf-state"
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


AWS_ELASTICSEARCH = """
resource "aws_elasticsearch_domain" "example" {{
  domain_name           = "{}"
  elasticsearch_version = "7.10"

  cluster_config {{
    instance_type = "t2.small.elasticsearch"
    instance_count = 3
  }}

  ebs_options {{
    ebs_enabled = true
    volume_size = 10
    volume_type = "gp2"
  }}
}}

output "aws_elasticsearch_endpoint" {{
    value = aws_elasticsearch_domain.example.endpoint
}}

"""

OPENSEARCH_ENDPOINT_RE = re.compile(r"aws_elasticsearch_endpoint = \"(.*)\"")


class AWSDataLakeDeployment1(DataLakeDeploymentInterface):
    def deploy_data_lake(self, project: ProjectDB, credentials: ProjectCredentialsDB):
        LOGGER.info("Creating AWS Data Lake Deployment 1")
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
        LOGGER.info(f"Creating S3 bucket with name {bucket_name}")
        with open(os.path.join(directory_path, "bucket.tf"), "w") as f:
            f.write(AWS_STORAGE.format(bucket_name))

        domain_name = (
            f"osdomain{''.join(str(uuid.uuid4()).split('-'))}"
            f"{''.join(str(project.id).split('-'))}"[:28]
        )
        LOGGER.info(f"Creating OpenSearch with Domain Name {domain_name}")
        with open(os.path.join(directory_path, "es.tf"), "w") as f:
            f.write(AWS_ELASTICSEARCH.format(domain_name))

        process = subprocess.run(
            ["terraform", f"-chdir={directory_path}", "apply", "-auto-approve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=this_env,
        )
        result = process.stdout.decode()
        LOGGER.debug(
            f"Terraform apply execution result:\n"
            f"stdout: '{process.stdout.decode()}'\n"
            f"stderr:{process.stderr.decode()}\n"
            f"exit code:{process.returncode}"
        )
        LOGGER.info("AWS Data Lake Deployment 1 created")
        opensearch_endpoint = OPENSEARCH_ENDPOINT_RE.search(result).group(1)
        return AWSDeployedResources1(
            s3={"bucket_name": bucket_name},
            opensearch={
                "domain_name": domain_name,
                "endpoint": opensearch_endpoint,
            },
        )

    def delete_data_lake(
        self,
        project: ProjectDB,
        credentials: ProjectCredentialsDB,
        project_deploy: ProjectDeployDB,
    ):
        LOGGER.info("Deleting AWS Data Lake Deployment 1")
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
        LOGGER.info("AWS Data Lake Deployment 1 deleted")
