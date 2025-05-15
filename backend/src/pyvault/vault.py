import os
from typing import Any, Dict, List

import hvac
from dotenv import load_dotenv

from .config import config

load_dotenv(".env.local")


class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=config.vault.url,
            token=config.vault.token,
            namespace=config.vault.namespace or None,
        )

    def __str__(self):
        result = self.client.sys.is_initialized()
        stringed = {
            "initialized": result["initialized"],
            "vault_token": result["vault_token"],
            "keys": result["keyts"],
            "keys_base64": result["keys_base64"],
        }
        # return f"initialized={stringed.initialized}, vault_token={stringed.vault_token}, keys={stringed.keys}, keys_base64={stringed.keys_base64}"
        return stringed

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

    def seal_vault(self) -> bool:
        """Seal the Vault"""
        self.client.sys.seal()
        status = self.client.sys.is_sealed()
        return status

    def is_sealed(self) -> bool:
        """Check if the vault is sealed"""
        sealed = self.client.sys.is_sealed()
        return sealed

    def initialize_vault(self, shares: int, threshold: int) -> str:
        """Initialize Hashi Vault if it isn't already, then get the root token and unseal keys.
        Vault will already be initialized with the bring up of the docker container,
        this is just
        """
        initialized = self.client.sys.is_initialized()

        if not (initialized):
            initialize = self.client.sys.initialize(
                secret_shares=shares, secret_threshold=threshold
            )
            return {
                "initialized": True,
                "keys": initialize["keys"],
                "keys_base64": initialize["keys_base64"],
                "root_token": initialize["root_token"],
            }
        else:
            return {
                "initialized": True,
                "root_token": "Vault has already been initialized.",
                "keys": "Vault has already been initialized",
                "keys_base64": "Vault has already been initialized",
            }

    def enable_aws_secrets_engine(self):
        """Enable AWS Secrets Engine in Vault"""
        try:
            engines_check = self.client.sys.list_mounted_secrets_engines()
            if "aws/" not in engines_check:
                self.client.sys.enable_secrets_engine(
                    backend_type="aws", path="aws", description="AWS Secrets Engine"
                )
                return {"status": "success", "message": "AWS Secrets Engine enabled!"}
            return {"status": "Info", "message": "AWS Secrets Engine already enabled."}
        except Exception as err:
            return {"status": "Error", "message": str(err)}

    def configure_aws_creds(self):  # leaving this out of .env and sticking to local env
        """Configure AWS IAM credentials for Vault"""

        self.enable_aws_secrets_engine()

        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

        if not aws_access_key or not aws_secret_key:
            return {
                "status": "Error",
                "message": "AWS Credentials were not found in environment variables",
            }
        try:
            response = self.client.secrets.aws.configure_root_iam_credentials(
                access_key=aws_access_key, secret_key=aws_secret_key
            )
            return response, {
                "status": "Success!",
                "message": "AWS Credentials configured!",
            }
        except Exception as err:
            return {"status": "Error", "message": str(err)}

    def rotate_aws_creds(self):
        """Rotate AWS IAM Credentials"""
        {self.client.secrets.aws.rotate_root_iam_credentials()}

    def create_aws_hvac_role(self, name: str, policy: Dict):
        """Create the IAM Role for Vault"""
        {
            self.client.secrets.aws.create_or_update_role(
                name=name,
                credential_type="assumed_role",
                policy_document=policy,
                policy_arn=["arn:aws:iam:aws:policy/AmazonVPCReadOnlyAccess"],
            )
        }

    def set_aws_lease(self, ttl: int):
        """Set the TTL Lease for AWS Secrets Engine"""
        self.client.secrets.aws.configure_lease(
            lease=f"{ttl}s",
        )

    def generate_aws_credentials(self, role_name: str):
        """Create credentials for named role, the role must exist before being queried"""
        if not role_name:
            role_name = "hvac-role"

        generate_creds_response = self.client.secrets.aws.generate_credentials(
            role_name
        )

        response = {
            "access_key_id": generate_creds_response["data"]["access_key"],
            "secret_key": generate_creds_response["data"]["secret_key"],
        }

        return response

    def delete_aws_role(self, role_name: str):
        """Delete AWS Role"""
        # to do: list roles and check to make sure role was deleted
        # to do: pop a confirm box to make sure it was not an errant click
        if not role_name:
            role_name = "hvac-role"

        response = self.client.secrets.aws.delete_role(name=role_name)
        return response

    def list_aws_roles(self):
        """List roles from AWS"""
        response = self.client.secrets.aws.list_roles()
        format_response = {"roles": response["data"]["keys"]}
        return format_response

    def pki_generate_root(
        self,
        type: str,
        CN: str,
        issuer: str,
        permitted_domains: str,
        ttl: int = 365,
        format: str = "pem",
    ):
        """Generate Root Cert"""
        if not type:
            type = "internal"
        if not issuer:
            issuer = "Sample Root"
        if not permitted_domains:
            permitted_domains = "nevermorelab.com"
        if not CN:
            CN = "test"

        generate_root = self.client.secrets.pki.generate_root(type=type, common_name=CN)
        return generate_root

    def pki_generate_intermediate(self, type: str, CN: str):
        """Generate Intermediate Cert"""
        generate_intermediate = self.client.secrets.pki.generate_intermediate(
            type=type, common_name=CN
        )
        return generate_intermediate

    def pki_list_certificates(self):
        """List certs in PKI Engine"""
        list_certificates = self.client.secrets.pki.list_certificates()
        return list_certificates

    def pki_generate_certificate(self, name: str, CN: str):
        """Create a certificate with the PKI engine"""
        generate_certificate = self.client.secrets.pki.generate_certificate(
            name=name, common_name=CN
        )
        return generate_certificate

    def pki_revoke_certificate(self, name: str, sn: str):
        """Revoke a certificate with the PKI engine"""
        revoke_certificate = self.client.secrets.pki.revoke_certificate(
            serial_number=sn
        )
        return revoke_certificate


# to do: add more try catch handling
