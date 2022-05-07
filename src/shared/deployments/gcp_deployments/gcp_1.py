import os
import subprocess
import uuid

from pydantic import BaseModel

from database.models import ProjectCredentialsDB, ProjectDB, ProjectDeployDB
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

GCP_BIGQUERY = """
resource "google_bigquery_dataset" "default" {{
  dataset_id                  = "{dataset_id}"
  friendly_name               = "Project Dataset"
  description                 = "This is a test description"
  location                    = "EU"
  default_table_expiration_ms = 3600000

  labels = {{
    env = "default"
  }}
}}

resource "google_bigquery_table" "default" {{
  dataset_id = google_bigquery_dataset.default.dataset_id
  table_id   = "{table_id}"

  time_partitioning {{
    type = "DAY"
  }}

  labels = {{
    env = "default"
  }}

  deletion_protection = false

  schema = <<EOF
[
  {{
    "name": "id",
    "type": "STRING",
    "mode": "REQUIRED"
  }},
  {{
    "name": "file",
    "type": "BYTES",
    "mode": "REQUIRED"
  }},
  {{
    "name": "name",
    "type": "STRING",
    "mode": "REQUIRED"
  }},
  {{
    "name": "type",
    "type": "STRING",
    "mode": "REQUIRED"
  }},
  {{
    "name": "size",
    "type": "INTEGER",
    "mode": "REQUIRED"
  }},
  {{
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  }},
  {{
    "name": "source",
    "type": "STRING",
    "mode": "REQUIRED"
  }},
  {{
    "name": "user_tags",
    "type": "RECORD",
    "mode": "REPEATED",
    "fields": [
        {{
            "name": "name",
            "type": "STRING",
            "mode": "REQUIRED"
        }},
        {{
            "name": "value",
            "type": "STRING",
            "mode": "NULLABLE"
        }}
    ]
  }},
  {{
    "name": "system_tags",
    "type": "RECORD",
    "mode": "REPEATED",
    "fields": [
        {{
            "name": "name",
            "type": "STRING",
            "mode": "REQUIRED"
        }},
        {{
            "name": "value",
            "type": "STRING",
            "mode": "NULLABLE"
        }}
    ]
  }}
]
EOF

}}
"""


class GCPDataLakeDeployment1(DataLakeDeploymentInterface):
    def deploy_data_lake(self, project: ProjectDB, credentials: ProjectCredentialsDB):
        LOGGER.info("Creating GCP Data Lake Deployment 1")
        gcp_project_id = credentials.credentials.project_id
        dataset_name = "".join(str(uuid.uuid4()).split("-"))
        table_name = "".join(str(uuid.uuid4()).split("-"))
        gcp_credentials_path = get_credentials_tmp_path(credentials.credentials)
        this_env = dict(os.environ, GOOGLE_APPLICATION_CREDENTIALS=gcp_credentials_path)

        directory_path = f"/usr/app/infrastructure/{project.id}"
        os.makedirs(directory_path, exist_ok=True)
        with open(os.path.join(directory_path, "state.tf"), "w") as f:
            tf_state_f = TF_STATE.format(str(project.id), str(gcp_project_id))
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

        LOGGER.info(
            f"Creating Big Query with dataset_name {dataset_name} and table_name {table_name}"
        )
        with open(os.path.join(directory_path, "bigquery.tf"), "w") as f:
            f.write(GCP_BIGQUERY.format(dataset_id=dataset_name, table_id=table_name))

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

        LOGGER.info("GCP Data Lake Deployment 1 created")
        return GCPDeployedResources1(
            bigquery={
                "project": gcp_project_id,
                "dataset": dataset_name,
                "table": table_name,
            }
        )

    def delete_data_lake(
        self,
        project: ProjectDB,
        credentials: ProjectCredentialsDB,
        project_deploy: ProjectDeployDB,
    ):
        LOGGER.info("Deleting GCP Data Lake Deployment 1")

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
        LOGGER.info("GCP Data Lake Deployment 1 deleted")
