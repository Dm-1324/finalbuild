FROM python:3.9-slim

# 1. Install only essential system dependencies
RUN apt-get update && \
    apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    # Required by soundfile (not pyaudio)
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Create app directory
WORKDIR /app

# 3. Install Python dependencies with explicit constraints
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt \
    # Explicitly block audio packages
    --ignore-installed pyaudio sounddevice && \
    python -c "import nltk; nltk.download('punkt', quiet=True)"

# 4. Copy app files
COPY . .

# 5. Create needed directories
RUN mkdir -p audio_outputs

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:$PORT", "-w", "4", "--timeout", "120"]