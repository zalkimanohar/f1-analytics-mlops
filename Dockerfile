FROM python:3.11-slim

WORKDIR /app

# System deps (if needed later, keep minimal for now)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Install Python deps
RUN pip install --upgrade pip \
 && pip install -r api/requirements.txt

# Expose API port
EXPOSE 8000

# Default command: run FastAPI app
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
