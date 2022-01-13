from shared.models import AWSProjectDeployType, GCPProjectDeployType
from shared.deployments.aws_deployments.aws_1 import AWSDataLakeDeployment1
from shared.deployments.gcp_deployments.gcp_1 import GCPDataLakeDeployment1
from shared.deployments.gcp_deployments.gcp_2 import GCPDataLakeDeployment2

DEPLOYMENT_CLASSES = {
    AWSProjectDeployType.AWS_1.value: AWSDataLakeDeployment1,
    GCPProjectDeployType.GCP_1.value: GCPDataLakeDeployment1,
    GCPProjectDeployType.GCP_2.value: GCPDataLakeDeployment2,
}
