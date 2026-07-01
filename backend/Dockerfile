# Stage 1: Build Stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies (e.g., for compiled C extensions if needed by asyncpg/sqlalchemy)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a local directory
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime Stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime libpq (needed by asyncpg underneath if not purely asyncpg native, though asyncpg is mostly native, libpq is good for psql tools)
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy installed dependencies from the builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Ensure the local bin is on the PATH
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy the application code
COPY . .

# Change ownership to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the API port
EXPOSE 8000

# Default command for production (can be overridden by docker-compose for dev)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
