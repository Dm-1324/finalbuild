from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile
import logging
from dotenv import load_dotenv
import nltk


nltk.download('punkt', quiet=True) 
# Initialize
load_dotenv()
app = Flask(__name__)
CORS(app)  # Allow CORS for all routes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Health Check Endpoint ---
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# --- Speech-to-Text Endpoint ---
@app.route('/stt', methods=['POST'])
def stt():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    try:
        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
            request.files['audio'].save(tmp.name)

            if os.getenv("ASSEMBLYAI_API_KEY"):
                from assemblyai_stt import transcribe_audio
                transcript, lang = transcribe_audio(tmp.name)
            else:
                from whisper_stt import transcribe_with_confidence
                transcript, lang = transcribe_with_confidence(tmp.name)

            return jsonify({
                "text": transcript,
                "language": lang,
                "status": "success"
            })

    except Exception as e:
        logger.error(f"STT failed: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- Text-to-Speech Endpoint ---
@app.route('/tts', methods=['POST'])
def tts():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing text"}), 400

    try:
        text = data['text']
        lang = data.get('language', 'en')
        output_file = f"tts_{hash(text)}.mp3"
        output_path = os.path.join("audio_outputs", output_file)

        # Choose TTS provider
        if os.getenv("ELEVENLABS_API_KEY"):
            from elevenlabs_tts import generate_speech
            success = generate_speech(text, lang, output_path)
            if not success:
                raise Exception("ElevenLabs TTS generation failed")
        else:
            from gtts import gTTS
            tts = gTTS(text=text, lang=lang)
            tts.save(output_path)

        return jsonify({
            "audio_url": f"{os.getenv('HOSTED_URL')}/audio/{output_file}",
            "status": "success"
        })

    except Exception as e:
        logger.error(f"TTS failed: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- AI Response Endpoint ---
@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({"error": "Missing messages"}), 400

    try:
        from openai_chat import get_ai_response
        response = get_ai_response(data['messages'])
        return jsonify({
            "response": response,
            "status": "success"
        })

    except Exception as e:
        logger.error(f"Generation failed: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# --- Serve Audio Files ---
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    try:
        return send_from_directory(
            os.path.abspath('audio_outputs'),
            filename,
            mimetype='audio/mpeg',
            as_attachment=False
        )
    except Exception as e:
        logger.error(f"Audio serve failed: {str(e)}")
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    os.makedirs("audio_outputs", exist_ok=True)
    app.run(host='0.0.0.0', port=5000)
