# Use Python 3.10 as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install UV
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml .
COPY src/ ./src/

# Create venv and install dependencies
RUN uv venv
#RUN uv pip install --no-cache-dir -e .
RUN pip install --no-cache-dir fastapi uvicorn hvac pydantic python-dotenv

# Expose API port
EXPOSE 8000

# Run the API
CMD ["python", "-m", "src.pyvault.main"]