import uvicorn

from .config import config


def main():
    """Run the API server"""
    uvicorn.run(
        "pyvault.api:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.debug,
    )


if __name__ == "__main__":
    main()
