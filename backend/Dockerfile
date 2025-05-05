# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed later, e.g., for specific libraries)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Consider using --no-cache-dir to reduce image size slightly
# Add --upgrade pip before install if needed
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using Uvicorn
# --host 0.0.0.0 makes it accessible from outside the container
# --reload is useful for development, remove for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
