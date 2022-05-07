from pydantic import BaseModel, constr, stricturl


class GCPCredentials(BaseModel):
    type: constr(max_length=256)
    project_id: constr(max_length=256)
    private_key_id: constr(min_length=40, max_length=40)
    private_key: constr(max_length=2096)
    client_email: constr(max_length=256)
    client_id: constr(min_length=21, max_length=21, regex=r"^\d+$")  # noqa
    auth_uri: stricturl(max_length=256)
    token_uri: stricturl(max_length=256)
    auth_provider_x509_cert_url: stricturl(max_length=256)
    client_x509_cert_url: stricturl(max_length=256)


class AWSCredentials(BaseModel):
    access_key_id: constr(max_length=256)
    secret_access_key: constr(max_length=256)


class AzureCredentials(BaseModel):
    tenant_id: constr(max_length=256)
    client_id: constr(max_length=100)
    client_secret: constr(max_length=100)
