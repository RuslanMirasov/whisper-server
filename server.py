from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uuid
import os
import wave
from whisper_model import transcribe

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    audio_data = bytearray()

    try:
        while True:
            chunk = await websocket.receive_bytes()
            audio_data.extend(chunk)

    except WebSocketDisconnect:
        audio_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.wav")
        with wave.open(audio_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data)

        text = transcribe(audio_path)
        await websocket.close()
        print(f"[+] Распознано: {text}")
        os.remove(audio_path)
