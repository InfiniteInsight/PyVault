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
    is_initialized: str
    root_token: str
    keys: str


class SealedStatus(BaseModel):
    sealed: str
