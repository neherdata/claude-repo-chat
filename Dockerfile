FROM python:3.13-slim

# Install git and git-crypt
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    git-crypt \
    && rm -rf /var/lib/apt/lists/*

# Install PDM
RUN pip install --no-cache-dir pdm

# Set working directory
WORKDIR /app

# Copy backend files
COPY backend/pyproject.toml backend/pdm.lock* ./

# Install dependencies
RUN pdm install --prod --no-lock --no-editable

# Copy application code
COPY backend/app ./app

# Create directories for repos and keys
RUN mkdir -p /tmp/repos /opt/claude-repo-chat/keys

# Expose port
EXPOSE 8080

# Run application
CMD ["pdm", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
