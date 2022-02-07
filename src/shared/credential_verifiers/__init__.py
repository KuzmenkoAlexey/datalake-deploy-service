from shared.credential_verifiers.google import verify_gcp_credentials
from shared.credential_verifiers.amazon import verify_aws_credentials
from shared.credential_verifiers.azure import verify_azure_credentials
from api.models import ProjectCredentialsCreate
from database.models import ProjectDB
from shared.models import ServiceProviderType


async def verify_credentials(
    project: ProjectDB, project_credentials: ProjectCredentialsCreate
):
    if project.service_provider == ServiceProviderType.GCP:
        return await verify_gcp_credentials(project_credentials)
    elif project.service_provider == ServiceProviderType.AWS:
        return await verify_aws_credentials(project_credentials)
    elif project.service_provider == ServiceProviderType.AZURE:
        return await verify_azure_credentials(project_credentials)
    return False
