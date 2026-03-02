from flask import Flask, request, jsonify
from flask_cors import CORS
import edge_tts
import asyncio
import base64
import tempfile
import os

app = Flask(__name__)
# Allows the React app to talk to this server
CORS(app)

async def generate_audio(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    await communicate.save(path)
    return path

@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text', 'Hello, this is a test.')
    voice = data.get('voice', 'en-IN-NeerjaNeural') 
    
    try:
        audio_path = asyncio.run(generate_audio(text, voice))
        with open(audio_path, 'rb') as audio_file:
            audio_b64 = base64.b64encode(audio_file.read()).decode('utf-8')
        os.remove(audio_path)
        return jsonify({'success': True, 'audio_base64': audio_b64})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "online", "message": "TTS Engine is ready!"})

if __name__ == '__main__':
    # Binds to the port Render provides
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
