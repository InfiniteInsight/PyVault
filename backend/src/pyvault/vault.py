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

    def initialize_vault(self, shares: int, threshold: int) -> Dict[str, Any]:
        """Initialize Hashi Vault if it isn't already, then get the root token and unseal keys.
        Vault will already be initialized with the bring up of the docker container,
        this is just for testing purposes
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
        """Enable the AWS secrets engine in Vault"""
        try:
            # Check if AWS secrets engine is already enabled
            enabled_engines = self.client.sys.list_mounted_secrets_engines()
            if "aws/" not in enabled_engines:
                self.client.sys.enable_secrets_engine(
                    backend_type="aws", path="aws", description="AWS secrets engine"
                )
                return {"status": "success", "message": "AWS secrets engine enabled"}
            return {
                "status": "success",
                "message": "AWS secrets engine already enabled",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def configure_aws_creds(self):
        """Configure AWS IAM credentials for Vault"""
        # First, ensure AWS secrets engine is enabled
        enable_result = self.enable_aws_secrets_engine()
        if enable_result.get("status") == "error":
            return enable_result

        # Debug output to check environment variables
        print("==== AWS Credentials Debugging ====")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        print(f"Environment variables: {dict(os.environ)}")
        print(
            f"AWS_ACCESS_KEY_ID exists: {'Yes' if os.environ.get('AWS_ACCESS_KEY_ID') else 'No'}"
        )
        print(
            f"AWS_SECRET_ACCESS_KEY exists: {'Yes' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'No'}"
        )

        # Try different ways to access environment variables
        aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

        # For testing purposes, if no real credentials are available, use test values
        if not aws_access_key or not aws_secret_key:
            # Use dummy values for development only
            print("WARNING: Using dummy AWS credentials for development")
            aws_access_key = "AKIAIOSFODNN7EXAMPLE"
            aws_secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

        try:
            print(
                f"Using AWS credentials: {aws_access_key[:4]}...{aws_access_key[-4:]}"
            )
            response = self.client.secrets.aws.configure_root_iam_credentials(
                access_key=aws_access_key,
                secret_key=aws_secret_key,
            )
            return {
                "status": "success",
                "message": "AWS credentials configured successfully",
            }
        except Exception as e:
            print(f"Error configuring AWS credentials: {str(e)}")
            return {"status": "error", "message": str(e)}

    def rotate_aws_creds(self):
        """Rotate AWS IAM Credentials"""
        try:
            response = self.client.secrets.aws.rotate_root_iam_credentials()
            return {
                "status": "success",
                "message": "AWS credentials rotated successfully",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_aws_hvac_role(self, name: str, policy: Dict):
        """Create the IAM Role for Vault"""
        try:
            if not name:
                name = "hvac-role"

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

            response = self.client.secrets.aws.create_or_update_role(
                name=name,
                credential_type="assumed_role",
                policy_document=policy,
                policy_arns=["arn:aws:iam:aws:policy/AmazonVPCReadOnlyAccess"],
            )
            return {
                "status": "success",
                "message": f"AWS role '{name}' created/updated successfully",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def set_aws_lease(self, ttl: int):
        """Set the TTL Lease for AWS Secrets Engine"""
        try:
            response = self.client.secrets.aws.configure_lease(
                lease=f"{ttl}s",
            )
            return {
                "status": "success",
                "message": f"AWS lease configured with TTL {ttl}s",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_aws_credentials(self, role_name: str):
        """Create credentials for named role, the role must exist before being queried"""
        try:
            if not role_name:
                role_name = "hvac-role"

            generate_creds_response = self.client.secrets.aws.generate_credentials(
                role_name
            )

            return {
                "access_key_id": generate_creds_response["data"]["access_key"],
                "secret_key": generate_creds_response["data"]["secret_key"],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_aws_role(self, role_name: str):
        """Delete AWS Role"""
        try:
            if not role_name:
                role_name = "hvac-role"

            response = self.client.secrets.aws.delete_role(name=role_name)
            return {
                "status": "success",
                "message": f"AWS role '{role_name}' deleted successfully",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_aws_roles(self):
        """List roles from AWS"""
        try:
            response = self.client.secrets.aws.list_roles()
            roles = response.get("data", {}).get("keys", [])
            return {"status": "success", "roles": roles}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def pki_generate_root(
        self,
        type: str = "internal",
        CN: str = "test.nevermorelab.com",
        issuer: str = "Sample Root",
        permitted_domains: str = "nevermorelab.com",
        ttl: int = 365,
        format: str = "pem",
    ):
        """Generate Root Cert"""
        try:
            generate_root = self.client.secrets.pki.generate_root(
                type=type, common_name=CN
            )
            return {"status": "success", "data": generate_root}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def pki_generate_intermediate(self, type: str, CN: str):
        """Generate Intermediate Cert"""
        try:
            generate_intermediate = self.client.secrets.pki.generate_intermediate(
                type=type, common_name=CN
            )
            return {"status": "success", "data": generate_intermediate}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def pki_list_certificates(self):
        """List certs in PKI Engine"""
        try:
            list_certificates = self.client.secrets.pki.list_certificates()
            return {"status": "success", "certificates": list_certificates}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def pki_generate_certificate(self, name: str, CN: str):
        """Create a certificate with the PKI engine"""
        try:
            generate_certificate = self.client.secrets.pki.generate_certificate(
                name=name, common_name=CN
            )
            return {"status": "success", "certificate": generate_certificate}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def pki_revoke_certificate(self, name: str, sn: str):
        """Revoke a certificate with the PKI engine"""
        try:
            revoke_certificate = self.client.secrets.pki.revoke_certificate(
                serial_number=sn
            )
            return {"status": "success", "data": revoke_certificate}
        except Exception as e:
            return {"status": "error", "message": str(e)}
