from faster_whisper import WhisperModel

model = WhisperModel("base", compute_type="int8")

def transcribe(audio_path):
    segments, _ = model.transcribe(audio_path, beam_size=5)
    result = " ".join([segment.text for segment in segments])
    return result.strip()
