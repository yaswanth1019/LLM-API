import socket
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import queue
import json
import os

model_path = "vosk-model-small-en-us-0.15"

if not os.path.exists(model_path):
    print("❌ Model not found!")
    exit(1)

model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print("⚠️ Audio error:", status)
    audio_queue.put(bytes(indata))

HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("🟢 Waiting for Unity to connect on port 65432...")
    conn, addr = s.accept()
    print(f"✅ Connected by {addr}")

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("🎙️ Listening...")

        try:
            while True:
                data = audio_queue.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        print("🗣️ Sending:", text)
                        conn.sendall((text + "\n").encode())
        except KeyboardInterrupt:
            print("🛑 Stopped by user")
