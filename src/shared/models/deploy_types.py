from enum import Enum


class AWSProjectDeployType(str, Enum):
    AWS_1 = "AWS_1"


class GCPProjectDeployType(str, Enum):
    GCP_1 = "GCP_1"
    GCP_2 = "GCP_2"


class AzureProjectDeployType(str, Enum):
    AZURE_1 = "AZURE_1"
