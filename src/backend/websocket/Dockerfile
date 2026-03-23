# RUN FROM THE ROOT DIRECTORY
FROM python:3.12-slim

WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy application code and install dependencies
COPY src/backend/websocket/ .
COPY src/frontend/src/agent/config.json ./config.json

RUN pip install --no-cache-dir -r requirements.txt

# Expose WebSocket port and health check port
EXPOSE 8081
EXPOSE 8082

# Run the server
CMD ["python", "server.py", "--enable-strands"]
