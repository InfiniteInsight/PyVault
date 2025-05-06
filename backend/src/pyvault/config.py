import os

from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()


class VaultConfig(BaseModel):
    url: str = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    token: str = os.getenv("VAULT_TOKEN", "")
    namespace: str = os.getenv("VAULT_NAMESPACE", "")


class ApiConfig(BaseModel):
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("API_DEBUG", "False").lower() == "true"


class Config:
    vault: VaultConfig = VaultConfig()
    api: ApiConfig = ApiConfig()


config = Config()
