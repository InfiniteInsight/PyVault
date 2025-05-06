from unittest.mock import patch

import pytest

from pyvault.vault import VaultClient


@pytest.fixture
def mock_hvac_client():
    with patch("hvac.Client") as mock_client:
        yield mock_client


def test_vault_health(mock_hvac_client):
    # Setup
    mock_instance = mock_hvac_client.return_value
    mock_instance.sys.read_health_status.return_value = {
        "initialized": True,
        "sealed": False,
        "version": "1.12.3",
    }

    # Execute
    client = VaultClient()
    health = client.get_health()

    # Assert
    assert health["status"] == "healthy"
    assert health["initialized"] is True
    assert health["sealed"] is False
    assert health["version"] == "1.12.3"


def test_list_secrets(mock_hvac_client):
    # Setup
    mock_instance = mock_hvac_client.return_value
    mock_instance.secrets.kv.v2.list_secrets.return_value = {
        "data": {"keys": ["secret1", "secret2"]}
    }

    # Execute
    client = VaultClient()
    secrets = client.list_secrets("path")

    # Assert
    assert secrets == ["secret1", "secret2"]
    mock_instance.secrets.kv.v2.list_secrets.assert_called_once_with(path="path")


def test_get_secret(mock_hvac_client):
    # Setup
    mock_instance = mock_hvac_client.return_value
    mock_instance.secrets.kv.v2.read_secret_version.return_value = {
        "data": {"data": {"key": "value"}}
    }

    # Execute
    client = VaultClient()
    secret = client.get_secret("path")

    # Assert
    assert secret == {"key": "value"}
    mock_instance.secrets.kv.v2.read_secret_version.assert_called_once_with(path="path")
