# Briefcase AI Demo Environment
# Uses Python 3.11 for optimal compatibility with briefcase-ai SDK

FROM python:3.11-slim

LABEL org.opencontainers.image.title="Briefcase AI Demo Environment"
LABEL org.opencontainers.image.description="Complete environment for running Briefcase AI governance demos"
LABEL org.opencontainers.image.version="1.0"

# Install system dependencies including OpenSSL for briefcase-ai compilation
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements-docker.txt .
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy demo files
COPY vantara-briefcase-demo/ ./vantara-briefcase-demo/
COPY regulatory-workflows/ ./regulatory-workflows/
COPY shared/ ./shared/
COPY README.md RUNNING_DEMOS.md ./

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user
RUN useradd -m -u 1000 demouser && chown -R demouser:demouser /app
USER demouser

# Default command
CMD ["bash"]

# Health check to ensure briefcase-ai is working
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 -c "import briefcase_ai; print('briefcase-ai OK')" || exit 1