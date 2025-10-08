# Use a stable and lightweight Python image
FROM python:3.11-slim

# Install system dependencies (required for Pillow, OpenCV, and Vulkan runtime)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
		libgomp1 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better build caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Download and install RealSR NCNN Vulkan binaries and models
RUN mkdir /tools && cd /tools && \
    wget https://github.com/nihui/realsr-ncnn-vulkan/releases/download/20220728/realsr-ncnn-vulkan-20220728-ubuntu.zip -O realsr.zip && \
    unzip realsr.zip && \
    mv realsr-ncnn-vulkan-20220728-ubuntu/realsr-ncnn-vulkan /usr/local/bin/realsr-ncnn-vulkan && \
    mv realsr-ncnn-vulkan-20220728-ubuntu/models-DF2K /usr/local/bin/models-DF2K && \
    mv realsr-ncnn-vulkan-20220728-ubuntu/models-DF2K_JPEG /usr/local/bin/models-DF2K_JPEG && \
    chmod +x /usr/local/bin/realsr-ncnn-vulkan && \
    rm -rf /tools/realsr.zip /tools/realsr-ncnn-vulkan-20220728-ubuntu

# Copy application source code
COPY ./app /app

# Expose app port
EXPOSE 8080

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]