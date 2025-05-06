from typing import Any, Dict, List

import hvac

from .config import config


class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=config.vault.url,
            token=config.vault.token,
            namespace=config.vault.namespace or None,
        )

    def get_health(self) -> Dict[str, Any]:
        """Get Vault health status"""
        health = self.client.sys.read_health_status(method="GET")
        return {
            "status": "healthy"
            if health["initialized"] and not health["sealed"]
            else "unhealthy",
            "initialized": health["initialized"],
            "sealed": health["sealed"],
            "version": health["version"],
        }

    def list_secrets(self, path: str) -> List[str]:
        """List secrets at a given path"""
        try:
            response = self.client.secrets.kv.v2.list_secrets(path=path)
            return response.get("data", {}).get("keys", [])
        except Exception:
            # If the path doesn't exist, return an empty list
            return []

    def get_secret(self, path: str) -> Dict[str, Any]:
        """Get a secret at a given path"""
        response = self.client.secrets.kv.v2.read_secret_version(path=path)
        return response.get("data", {}).get("data", {})

    def create_update_secret(self, path: str, data: Dict[str, str]) -> bool:
        """Create or update a secret at a given path"""
        self.client.secrets.kv.v2.create_or_update_secret(path=path, secret=data)
        return True

    def delete_secret(self, path: str) -> bool:
        """Delete a secret at a given path"""
        self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=path)
        return True
