from fastapi import FastAPI, WebSocket
import asyncio
import subprocess
import numpy as np
from faster_whisper import WhisperModel
import struct

app = FastAPI()

# Загружаем модель (можно поменять "base" на "small", "medium", "large")
model = WhisperModel("base", compute_type="int8")

# Запускаем ffmpeg для преобразования входящего потока
def start_ffmpeg():
    return subprocess.Popen(
        [
            "ffmpeg",
            "-loglevel", "quiet",
            "-f", "webm",
            "-i", "pipe:0",
            "-ac", "1",
            "-ar", "16000",
            "-f", "s16le",
            "pipe:1",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

@app.websocket("/ws/transcribe")
async def transcribe_websocket(websocket: WebSocket):
    await websocket.accept()
    print("✅ Client connected")

    ffmpeg = start_ffmpeg()
    pcm_buffer = bytearray()
    transcription_buffer = ""

    try:
        while True:
            chunk = await websocket.receive_bytes()
            ffmpeg.stdin.write(chunk)

            # Читаем из stdout ffmpeg
            while ffmpeg.stdout.readable():
                raw = ffmpeg.stdout.read(3200)  # ~100ms аудио при 16kHz, 16bit mono
                if not raw:
                    break

                # Преобразуем байты в float32 numpy массив
                pcm = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0

                if len(pcm) == 0:
                    continue

                # Распознаём без сегментации (чтобы не ждать окончания предложения)
                segments, _ = model.decode(pcm)
                text = "".join([s.text for s in segments]).strip()

                if text and text != transcription_buffer:
                    transcription_buffer = text
                    await websocket.send_text(text)

    except Exception as e:
        print("❌ Ошибка:", e)
    finally:
        try:
            ffmpeg.kill()
        except:
            pass
        await websocket.close()
        print("🛑 Client disconnected")
