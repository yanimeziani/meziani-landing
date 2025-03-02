FROM python:3.11.9

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
COPY pyproject.toml .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir flask  # Add Flask for the dashboard

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Copy the application code
COPY . .

# Create data directory for memory DB storage
RUN mkdir -p /app/data && chmod 777 /app/data

# Create log directory
RUN mkdir -p /app/logs && chmod 777 /app/logs

# Add a healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Expose the app port
EXPOSE 5000

# Run the Flask application
CMD ["python", "src/app.py"]