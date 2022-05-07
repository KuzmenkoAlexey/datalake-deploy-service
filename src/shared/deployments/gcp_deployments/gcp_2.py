import os
import subprocess
import uuid

from pydantic import BaseModel

from database.models import ProjectCredentialsDB, ProjectDB, ProjectDeployDB
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

# Configure the GCP Provider
provider "google" {{
  project     = "{}"
  region      = "us-central1"
}}

"""

GCP_BIGTABLE = """
resource "google_bigtable_instance" "instance" {{
  name = "{instance_id}"
  deletion_protection = false

  cluster {{
    cluster_id   = "{cluster_id}"
    zone         = "us-central1-a"
    num_nodes    = 1
    storage_type = "HDD"
  }}

  lifecycle {{
    prevent_destroy = false
  }}
}}

resource "google_bigtable_table" "table" {{
  name          = "{table_id}"
  instance_name = google_bigtable_instance.instance.name

  lifecycle {{
    prevent_destroy = false
  }}
}}
"""

GCP_CLOUD_STORAGE = """
resource "google_storage_bucket" "data_lake_storage" {{
  name          = "{bucket_name}"
  location      = "US"
  force_destroy = true
}}
"""


class GCPDataLakeDeployment2(DataLakeDeploymentInterface):
    def deploy_data_lake(self, project: ProjectDB, credentials: ProjectCredentialsDB):
        LOGGER.info("Creating GCP Data Lake Deployment 2")

        gcp_project_id = credentials.credentials.project_id

        directory_path = f"/usr/app/infrastructure/{project.id}"
        os.makedirs(directory_path, exist_ok=True)
        gcp_credentials_path = get_credentials_tmp_path(credentials.credentials)
        this_env = dict(os.environ, GOOGLE_APPLICATION_CREDENTIALS=gcp_credentials_path)
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

        with open(os.path.join(directory_path, "state.tf"), "w") as f:
            tf_state_f = TF_STATE.format(str(project.id), str(gcp_project_id))
            f.write(tf_state_f)

        instance_id = "in" + "".join(str(uuid.uuid4()).split("-"))[:10]
        table_id = "table" + "".join(str(uuid.uuid4()).split("-"))[:10]
        cluster_id = "clust" + "".join(str(uuid.uuid4()).split("-"))[:10]

        bucket_name = "bucket" + "".join(str(uuid.uuid4()).split("-"))[:10]

        LOGGER.info(
            f"Creating Big Table with instance_id {instance_id}, table_id {table_id} and cluster_id {cluster_id}"
        )
        with open(os.path.join(directory_path, "bigtable.tf"), "w") as f:
            f.write(
                GCP_BIGTABLE.format(
                    instance_id=instance_id, table_id=table_id, cluster_id=cluster_id
                )
            )

        LOGGER.info(f"Creating Cloud Storage with bucket_name {bucket_name}")
        with open(os.path.join(directory_path, "bucket.tf"), "w") as f:
            f.write(GCP_CLOUD_STORAGE.format(bucket_name=bucket_name))

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

        LOGGER.info("GCP Data Lake Deployment 2 created")
        return GCPDeployedResources2(
            bigtable={
                "project": gcp_project_id,
                "cluster": cluster_id,
                "instance": instance_id,
                "table": table_id,
            },
            cloud_storage={"bucket": bucket_name},
        )

    def delete_data_lake(
        self,
        project: ProjectDB,
        credentials: ProjectCredentialsDB,
        project_deploy: ProjectDeployDB,
    ):
        LOGGER.info("Deleting GCP Data Lake Deployment 2")

        gcp_credentials_path = get_credentials_tmp_path(credentials.credentials)
        this_env = dict(os.environ, GOOGLE_APPLICATION_CREDENTIALS=gcp_credentials_path)
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

        LOGGER.info("GCP Data Lake Deployment 2 deleted")
