# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app
COPY app/templates/ ./templates
COPY app/static/ ./static

# Expose Flask port
EXPOSE 8080

# Use entrypoint script to load environment variables
# Using "flask run" or running the module directly
CMD ["python", "app/server.py"]

