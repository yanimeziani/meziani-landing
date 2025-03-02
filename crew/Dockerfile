FROM python:3.11.9

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install flask  # Add Flask for the dashboard

# Set environment variables
ENV PYTHONPATH=/app/src

# Copy the application code
COPY . .

# Create data directory for memory DB storage
RUN mkdir -p /app/data && chmod 777 /app/data

# Expose the app port
EXPOSE 5000

# Run the Flask application
CMD ["python", "src/app.py"]