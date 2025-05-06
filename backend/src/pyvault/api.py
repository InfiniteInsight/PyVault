from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import HealthStatus, Secret, SecretData, SecretList
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/secrets/{path:path}", response_model=SecretList)
async def list_secrets(
    path: str, vault_client: VaultClient = Depends(get_vault_client)
):
    """List secrets at a given path"""
    try:
        secrets = vault_client.list_secrets(path)
        return {"paths": secrets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/secret/{path:path}", response_model=Secret)
async def get_secret(path: str, vault_client: VaultClient = Depends(get_vault_client)):
    """Get a secret at a given path"""
    try:
        data = vault_client.get_secret(path)
        return {"path": path, "data": data}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Secret not found: {str(e)}")


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
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/secret/{path:path}")
async def delete_secret(
    path: str, vault_client: VaultClient = Depends(get_vault_client)
):
    """Delete a secret at a given path"""
    try:
        vault_client.delete_secret(path)
        return {"message": f"Secret {path} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
