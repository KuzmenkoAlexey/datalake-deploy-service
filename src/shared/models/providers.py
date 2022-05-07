from enum import Enum


class ServiceProviderType(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"
