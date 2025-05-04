# voice_server.py
from flask import Flask, request, jsonify, send_file
import speech_recognition as sr
import pyttsx3
import os

app = Flask(__name__)

INPUT_WAV = "input.wav"
OUTPUT_WAV = "output.wav"

@app.route('/stt', methods=['POST'])
def speech_to_text():
    # save incoming audio
    with open(INPUT_WAV, "wb") as f:
        f.write(request.data)

    recognizer = sr.Recognizer()
    with sr.AudioFile(INPUT_WAV) as src:
        audio = recognizer.record(src)
        try:
            text = recognizer.recognize_google(audio)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"text": text})


@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # init engine
    engine = pyttsx3.init()
    # (optional) adjust voice/rate here:
    # engine.setProperty('rate', 150)
    # engine.setProperty('voice', someVoiceId)
    engine.save_to_file(text, OUTPUT_WAV)
    engine.runAndWait()

    if not os.path.exists(OUTPUT_WAV):
        return jsonify({"error": "TTS generation failed"}), 500

    return send_file(OUTPUT_WAV, mimetype='audio/wav')


if __name__ == '__main__':
    # remove debug to avoid auto‑reload issues
    app.run(host='0.0.0.0', port=5005)
