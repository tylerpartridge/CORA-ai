# Minimal Dockerfile for CORA FastAPI app
# Safe for collaborative restoration - no destructive steps

FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements
COPY data/requirements.txt ./requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 