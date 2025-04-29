FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (for better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt && \
    python -c "import nltk; nltk.download('punkt', quiet=True)"

# Copy the rest of the app
COPY . .

# Create the audio outputs directory
RUN mkdir -p audio_outputs

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:$PORT", "-w", "4", "--timeout", "120"]