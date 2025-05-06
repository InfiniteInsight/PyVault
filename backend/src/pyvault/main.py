import uvicorn

from src.pyvault.api import app
from src.pyvault.config import config


def main():
    """Run the API server"""
    uvicorn.run(
        # "pyvault.api:app",
        app,
        host=config.api.host,
        port=config.api.port,
        reload=config.api.debug,
    )


if __name__ == "__main__":
    main()
