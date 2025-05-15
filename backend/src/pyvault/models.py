from typing import Dict, List, Optional

from pydantic import BaseModel


class SecretData(BaseModel):
    data: Dict[str, str]


class Secret(BaseModel):
    path: str
    data: Dict[str, str]


class SecretList(BaseModel):
    paths: List[str]


class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None


class HealthStatus(BaseModel):
    status: str
    initialized: bool
    sealed: bool
    version: str


class InitializeVault(BaseModel):
    initialized: Optional[bool]
    root_token: Optional[str]
    keys: Optional[List[str]] | Optional[str]
    keys_base64: Optional[List[str]] | Optional[str]


class SealedStatus(BaseModel):
    sealed: bool


class GeneratedAWSCreds(BaseModel):
    access_key_id: str
    secret_key: str
