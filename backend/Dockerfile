FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default port (Railway will override with $PORT)
ENV PORT=8000

# Expose port
EXPOSE $PORT

# Run the application - use shell form to expand $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT

