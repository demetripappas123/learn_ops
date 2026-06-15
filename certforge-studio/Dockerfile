# CertForge Studio — Streamlit UI container for Azure Container Apps.
# Build in the cloud with:  az acr build --registry <acr> --image certforge:latest .
FROM python:3.12-slim

WORKDIR /app

# Install core + Azure extras. Pure-Python deps, so the slim image is enough.
COPY requirements.txt requirements-azure.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-azure.txt

COPY . .

# Run as a non-root user (CWE-250: least privilege inside the container).
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Azure Container Apps routes ingress to this target port.
EXPOSE 8501

ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
