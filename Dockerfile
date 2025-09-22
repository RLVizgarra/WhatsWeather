# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ .

# Expose port (change if your app uses a different port)
EXPOSE 5000

# Run the application (replace with your actual entrypoint)
CMD ["python", "main.py"]