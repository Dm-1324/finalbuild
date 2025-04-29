FROM python:3.9-slim

# 1. Install only essential system dependencies
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 2. Create app directory first for better caching
WORKDIR /app

# 3. Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt && \
    python -c "import nltk; nltk.download('punkt', quiet=True)"

# 4. Copy app files
COPY . .

# 5. Create needed directories
RUN mkdir -p audio_outputs

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:$PORT", "-w", "4", "--timeout", "120"]