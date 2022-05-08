from shared.deployments.aws_deployments.aws_1 import AWSDataLakeDeployment1
from shared.deployments.aws_deployments.aws_2 import AWSDataLakeDeployment2
from shared.deployments.azure_deployments.azure_1 import AzureDataLakeDeployment1
from shared.deployments.gcp_deployments.gcp_1 import GCPDataLakeDeployment1
from shared.deployments.gcp_deployments.gcp_2 import GCPDataLakeDeployment2
from shared.deployments.gcp_deployments.gcp_3 import GCPDataLakeDeployment3
from shared.models.deploy_types import (
    AWSProjectDeployType,
    AzureProjectDeployType,
    GCPProjectDeployType,
)

DEPLOYMENT_CLASSES = {
    AWSProjectDeployType.AWS_1: AWSDataLakeDeployment1,
    AWSProjectDeployType.AWS_2: AWSDataLakeDeployment2,
    GCPProjectDeployType.GCP_1: GCPDataLakeDeployment1,
    GCPProjectDeployType.GCP_2: GCPDataLakeDeployment2,
    GCPProjectDeployType.GCP_3: GCPDataLakeDeployment3,
    AzureProjectDeployType.AZURE_1: AzureDataLakeDeployment1,
}
