FROM python:3.11-slim

# Set working directory to backend
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy root requirements (for ri_ctc_calc package)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend requirements
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy the entire application structure
COPY ri_ctc_calc /app/ri_ctc_calc
COPY backend /app/backend

# Set Python path to include the root directory
ENV PYTHONPATH=/app

# Set working directory to backend for proper imports
WORKDIR /app/backend

# Expose port (Cloud Run uses PORT env var)
ENV PORT=8080
EXPOSE 8080

# Run the FastAPI application from backend directory
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
