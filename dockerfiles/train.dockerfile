FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install system dependencies required by OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*


COPY pyproject.toml uv.lock README.md ./
COPY configs configs/

RUN uv sync --frozen --no-install-project

COPY src src/

RUN uv sync --frozen

ENTRYPOINT ["uv", "run", "python", "-m", "forestfires_project.train"]

