FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 wget unzip && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download realsr-ncnn-vulkan (for image upscaling)
RUN mkdir /tools && cd /tools && \
    wget https://github.com/nihui/realsr-ncnn-vulkan/releases/download/20220728/realsr-ncnn-vulkan-20220728-ubuntu.zip -O realsr.zip && \
    apt-get update && apt-get install -y unzip && \
    unzip realsr.zip && \
    mv realsr-ncnn-vulkan /usr/local/bin/realsr-ncnn-vulkan && \
    chmod +x /usr/local/bin/realsr-ncnn-vulkan

# Copy app
COPY ./app /app

# Expose port
EXPOSE 8080

# Run FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]