from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    GeneratedAWSCreds,
    HealthStatus,
    InitializeVault,
    SealedStatus,
    Secret,
    SecretData,
    SecretList,
)
from .vault import VaultClient

app = FastAPI(
    title="PyVault API", description="API for interacting with HashiCorp Vault"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # unsafe for dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_vault_client():
    return VaultClient()


@app.get("/health", response_model=HealthStatus)
async def health(vault_client: VaultClient = Depends(get_vault_client)):
    """Get API and Vault health status"""
    try:
        health_status = vault_client.get_health()
        return health_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/sealed", response_model=SealedStatus)
async def sealed(vault_client=Depends(get_vault_client)):
    """Check if the vault is sealed"""
    sealed_status = vault_client.is_sealed()
    return {"sealed": sealed_status}


@app.get("/secrets/{path:path}", response_model=SecretList)
async def list_secrets(
    path: str, vault_client: VaultClient = Depends(get_vault_client)
):
    """List secrets at a given path"""
    try:
        secrets = vault_client.list_secrets(path)
        return {"paths": secrets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/secret/{path:path}", response_model=Secret)
async def get_secret(path: str, vault_client: VaultClient = Depends(get_vault_client)):
    """Get a secret at a given path"""
    try:
        data = vault_client.get_secret(path)
        return {"path": path, "data": data}
    except Exception as e:
        raise HTTPException(
            status_code=404, detail=f"Secret not found: {str(e)}"
        ) from e


@app.post("/secret/{path:path}", response_model=Secret)
async def create_update_secret(
    path: str,
    secret_data: SecretData,
    vault_client: VaultClient = Depends(get_vault_client),
):
    """Create or update a secret at a given path"""
    try:
        vault_client.create_update_secret(path, secret_data.data)
        return {"path": path, "data": secret_data.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.delete("/secret/{path:path}")
async def delete_secret(
    path: str, vault_client: VaultClient = Depends(get_vault_client)
):
    """Delete a secret at a given path"""
    try:
        vault_client.delete_secret(path)
        return {"message": f"Secret {path} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/seal", response_model=SealedStatus)
async def seal_vault(vault_client: VaultClient = Depends(get_vault_client)):
    """Seal the vault"""
    sealed_status = vault_client.seal_vault()
    return {"sealed": sealed_status}


@app.post("/initialize", response_model=InitializeVault)
async def initialize_vault(
    shares: int = 5,
    threshold: int = 3,
    vault_client: VaultClient = Depends(get_vault_client),
):
    """Initialize Hashi Vault"""
    # root_token, keys, keys_base64, is_initialized = vault_client.initialize_vault(
    result = vault_client.initialize_vault(shares, threshold)

    return result


@app.post("/enable_aws_secrets_engine")
async def enable_aws_secrets_engine(
    vault_client: VaultClient = Depends(get_vault_client),
):
    """Enable AWS Secrets Engine in Vault"""
    response = vault_client.enable_aws_secrets_engine()
    return response


@app.post("/create_aws_hvac_role")
async def create_aws_hvac_role(
    policy: str,
    name: str,
    vault_client: VaultClient = Depends(get_vault_client),
):
    """Create the Vault role with access to describe EC2"""
    if not policy:
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Resource": "*",
                    "Action": "ec2:Describe*",
                    "Effect": "Allow",
                },
            ],
        }
    if not name:
        name = "hvac-role"

    vault_client.create_aws_hvac_role(policy)


@app.post("/set_aws_lease")
async def set_aws_lease(
    ttl: int, vault_client: VaultClient = Depends(get_vault_client)
):
    vault_client.set_aws_lease(ttl=ttl)


@app.post("/generate_aws_credentials", response_model=GeneratedAWSCreds)
async def generate_aws_credentials(
    role_name: str,
    vault_client: VaultClient = Depends(get_vault_client),
):
    response = vault_client.generate_aws_credentials(role_name=role_name)

    return response


@app.delete("/delete_aws_role")
async def delete_aws_role(
    role_name: str, vault_client: VaultClient = Depends(get_vault_client)
):
    response = vault_client.delete_aws_role(role_name=role_name)
    return response


@app.get("/list_aws_roles")
async def list_aws_roles(vault_client: VaultClient = Depends(get_vault_client)):
    response = vault_client.list_aws_roles()
    return response


@app.post("/rotate_aws_creds")
async def rotate_aws_creds(vault_client: VaultClient = Depends(get_vault_client)):
    response = vault_client.rotate_aws_creds()
    return response


@app.post("/configure_aws_creds")
async def configure_aws_creds(vault_client: VaultClient = Depends(get_vault_client)):
    response = vault_client.configure_aws_creds()
    return response


@app.post("/enable_pki_engine")
async def enable_pki_engine(vault_client: VaultClient = Depends(get_vault_client)):
    response = vault_client.enable_pki_engine()
    return response


@app.post("/pki_generate_root")
async def pki_generate_root(vault_client: VaultClient = Depends(get_vault_client)):
    response = vault_client.pki_generate_root(
        CN="test.nevermorelab.com", cert_type="internal", ttl=365, format="pem"
    )
    return response


@app.post("/pki_generate_intermediate")
async def pki_generate_intermediate(
    vault_client: VaultClient = Depends(get_vault_client),
):
    response = vault_client.pki_generate_intermediate(
        CN="intermediate.nevermorelab.com",
        cert_type="internal",
    )

    return response


@app.post("/pki_sign_certificate")
async def pki_sign_certificate(
    CN: str, CSR: str, vault_client: VaultClient = Depends(get_vault_client)
):
    if not CN:
        CN = "test-cert.nevermorelab.com"

    if not CSR:
        CSR = """
                    -----BEGIN CERTIFICATE REQUEST-----
            MIICojCCAYoCAQAwJTEjMCEGA1UEAxMadGVzdC1jZXJ0Lm5ldmVybW9yZWxhYi5j
            b20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDpUKN2bX+8gBSXz1Yx
            1Byoj5ao9CIgqo962E/L/iFHl8Q5Bk3+veZ5oGUj7ftVTMjeJG3mjOtNuqNnN92J
            0talQDC6jk8Xsx9pSGHYdn6XidTlXic8lwgZstXD0KxqngHoxch0QhNzkOqUrMLu
            MSyXRLG3WLODJpAXkOOWm2bSY1VgI/QRXKAdmT+CnmdB3A/BAXVcOBiBBZV8Ha2j
            kq/1Ni2NCq8JTGIs70FwkYQnI4jsxbP/R4liNXQIAztv6GuEWBtPtOWZrQYvSl6E
            d2uHvbmPefyg5YinG3yCrBRSTDqgDOhmqaNkTx8x3RIAB8nRbnJE5FSOaE250vUQ
            bi8hAgMBAAGgODA2BgkqhkiG9w0BCQ4xKTAnMCUGA1UdEQQeMByCGnRlc3QtY2Vy
            dC5uZXZlcm1vcmVsYWIuY29tMA0GCSqGSIb3DQEBCwUAA4IBAQC7lL2Id2uWvnM4
            NP7id6Bj/yJIqcSNSqHaX8UvNn3MyJm4h/DhwRCaM+I/UJezx/OXQX5RWYIsiS05
            /BepcFvVVLGjp4jTlZ06vSl6b1bXqbObGSJHnAs1AFLuliowkXJQwjYykXSuxzTV
            TGSh8JognMXDUwjwjzy16ICCwfD97JjokTR1e+5JEF02qcIDbmOuQ6onNaMKF7cC
            heHce/HGL4raEPgYreYWfSALqUr41mDwuMvVk1fZXpU8OpMrN81MRy0GnuPT3pgR
            fojJahAtTffY4Hv6RSLRZeVMCISiEHnkNw2ijYEuJWwJx3+CJAnbT6uI+pUtetBq
            Sr7pHxV4
            -----END CERTIFICATE REQUEST-----
            """

    response = vault_client.pki_sign_certificate(CSR=CSR, CN=CN)

    return response


# to do: When vault is sealed and "refresh status" is pressed, update the status table
# there is a bug where when the vault is sealed and then unsealed the refresh status button
# does not work it fails to fetch health status.
# also add more docstrings
