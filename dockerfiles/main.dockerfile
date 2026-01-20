# Dockerfile for Forest Fire Detection Pipeline
# Runs the full pipeline: sync -> train -> evaluate -> visualize

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for OpenCV, torch, GCS tools, and gcsfuse
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl \
    gnupg \
    && echo "deb http://packages.cloud.google.com/apt gcsfuse-`lsb_release -c -s` main" > /etc/apt/sources.list.d/gcsfuse.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
    && apt-get update && apt-get install -y gcsfuse \
    && rm -rf /var/lib/apt/lists/*

# Install Google Cloud SDK for gsutil (used in sync_data.py)
RUN curl -sSL https://sdk.cloud.google.com | bash -s -- --disable-prompts --install-dir=/opt
ENV PATH="/opt/google-cloud-sdk/bin:${PATH}"

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock* README.md ./
COPY src/ ./src/

# Install dependencies using uv (CPU-only PyTorch)
# Increase timeout for large package downloads
ENV UV_HTTP_TIMEOUT=120
RUN uv sync --frozen --no-dev

# Copy configuration files
COPY configs/ ./configs/

# Copy main entry point
COPY main.py ./

# Copy pretrained model weights if available
COPY yolov8n.pt ./

# Create necessary directories
RUN mkdir -p data models reports/figures reports/eval_results logs runs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default config path
ENV CONFIG_PATH=configs/config.yaml

# Copy and set up entrypoint script (fetches secrets from GCP)
COPY dockerfiles/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port for potential API usage
EXPOSE 8000

# Default command: run full pipeline
# Override with --pipeline train|evaluate|visualize|sync as needed
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["--pipeline", "all", "--config", "configs/config.yaml"]