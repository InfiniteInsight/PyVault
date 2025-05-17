import os

from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables from .env file in docker container or locally

for env_file in [".env.local", ".env"]:
    if os.path.exists(env_file):
        print(f"Loading environment from {env_file}")
        load_dotenv(env_file)
        break

# Debug
print(f"VAULT_ADDR: {os.environ.get('VAULT_ADDR')}")
print(
    f"AWS_ACCESS_KEY_ID exists: {
        'Yes' if os.environ.get('AWS_ACCESS_KEY_ID') else 'No'
    }"
)


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


class AWSSecretEngine:
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")


config = Config()
