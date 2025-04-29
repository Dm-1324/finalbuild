import os
import logging
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

def transcribe_with_confidence(file_path):
    """Faster Whisper implementation with CPU optimization"""
    try:
        logger.debug(f"Starting Whisper processing: {file_path}")
        
        # Load model with CPU optimizations
        model = WhisperModel(
            "small",  # Using smaller model for faster CPU processing
            device="cpu",
            compute_type="int8",  # Better for CPU
            download_root="./models"
        )
        
        segments, info = model.transcribe(file_path, beam_size=5)
        logger.debug(f"Detected language: {info.language}")
        
        # Combine segments
        transcript = " ".join([segment.text for segment in segments])
        return transcript, info.language
        
    except Exception as e:
        logger.error(f"Whisper error: {str(e)}")
        raise