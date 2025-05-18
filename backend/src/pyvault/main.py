import uvicorn

from .api import app
from .config import config


def main():
    """Run the API server"""
    uvicorn.run(
        # "pyvault.api:app",
        app,
        host=config.api.host,
        port=config.api.port,
        # reload=config.api.debug, #uncomment for local dev only, not for docker.
    )


if __name__ == "__main__":
    main()
