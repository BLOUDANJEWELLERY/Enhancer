# Base image with Python and system deps
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget git libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Real-ESRGAN precompiled binary (CPU)
RUN mkdir /tools && \
    cd /tools && \
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5/realesrgan-ncnn-vulkan-20220424-ubuntu.zip && \
    apt-get update && apt-get install -y unzip && \
    unzip realesrgan-ncnn-vulkan-20220424-ubuntu.zip && \
    mv realesrgan-ncnn-vulkan /usr/local/bin/realesrgan-ncnn-vulkan && \
    chmod +x /usr/local/bin/realesrgan-ncnn-vulkan

COPY ./app /app

EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]