FROM python:3.11.9

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set the PYTHONPATH to include src/
ENV PYTHONPATH=/app/src

# Copy the application code
COPY . .

# Create data directory for memory DB storage
RUN mkdir -p /app/data && chmod 777 /app/data

# Expose the app port
EXPOSE 5000

# Check if the crewai command is available
RUN pip show crewai || echo "Warning: crewai package not found!"

# Run the crewai command if available, otherwise fall back to a Python script
CMD if command -v crewai > /dev/null; then \
      crewai run; \
    else \
      python src/app.py; \
    fi