from enum import Enum


class AWSProjectDeployType(str, Enum):
    AWS_1 = "AWS_1"
    AWS_2 = "AWS_2"


class GCPProjectDeployType(str, Enum):
    GCP_1 = "GCP_1"
    GCP_2 = "GCP_2"
    GCP_3 = "GCP_3"


class AzureProjectDeployType(str, Enum):
    AZURE_1 = "AZURE_1"
