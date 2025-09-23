# Use official Python image as base
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# Copy application code
COPY app/ .

# Set environment variables (these can also be set via a .env file)
ENV WHATSAPP_ACCESS_TOKEN=${WHATSAPP_ACCESS_TOKEN}
ENV WHATSAPP_PHONE_NUMBER_ID=${WHATSAPP_PHONE_NUMBER_ID}
ENV WHATSAPP_TO_PHONE_NUMBER=${WHATSAPP_TO_PHONE_NUMBER}

# Run the application (replace with your actual entrypoint)
CMD ["python", "main.py"]