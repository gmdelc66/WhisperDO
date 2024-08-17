# crear múltiples archivos cuando se detecta voz.
# El programa creará un nuevo archivo si hay una pausa mayor a un número determinado de segundos o
# si el usuario dice "point".
# Los archivos estarán nombrados con el formato yyyymmddhhmmss, correspondiente a la fecha y hora
# de inicio de cada grabación:

import os
import pyaudio
import wave
import time
from datetime import datetime
import whisper
import numpy as np

# Inicializar el modelo Whisper
model = whisper.load_model("base")

# Directorios de salida
OUTPUT_DIR = "escucha/"
CONVERSA_DIR = "conversa/"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CONVERSA_DIR, exist_ok=True)

# Configuración de la grabación
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 16000
CHUNK = 1024
SILENCE_THRESHOLD = 2  # Segundos de silencio para detectar pausa
NO_VOICE_TIMEOUT = 10  # Segundos sin voz para finalizar el programa

# Inicializa PyAudio
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Escuchando...")

frames = []
recording = False
last_voice_time = time.time()

def save_recording(frames, start_time):
    """Guarda la grabación en un archivo WAV con un nombre basado en la fecha y hora."""
    if not frames:
        return
    filename = start_time.strftime("%Y%m%d%H%M%S") + ".wav"
    file_path = os.path.join(OUTPUT_DIR, filename)
    with wave.open(file_path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print(f"Grabación guardada en {file_path}")

    # Convertir a texto usando Whisper
    result = model.transcribe(file_path)
    text = result['text']
    if text.strip():  # Guardar solo si hay algo transcrito
        with open(os.path.join(CONVERSA_DIR, filename.replace(".wav", ".txt")), "w") as f:
            f.write(text)
        print(f"Transcripción guardada en {CONVERSA_DIR}")
    else:
        # os.remove(file_path)  # Eliminar el archivo de audio si no hay texto transcrito
        print("No se detectó voz, archivo eliminado.")

def reset_recording():
    """Resetea los datos de la grabación."""
    global frames, recording
    frames = []
    recording = False

def detect_voice(audio_data):
    """Detecta si hay voz en el audio utilizando un umbral de energía."""
    audio_array = np.frombuffer(audio_data, np.int16)
    energy = np.sum(audio_array ** 2) / len(audio_array)
    return energy > SILENCE_THRESHOLD

def main():
    global last_voice_time, recording
    try:
        start_time = None
        while True:
            data = stream.read(CHUNK)
            if detect_voice(data):
                frames.append(data)
                last_voice_time = time.time()
                if not recording:
                    print("Voz detectada, iniciando grabación...")
                    start_time = datetime.now()
                    recording = True
            elif recording:
                if time.time() - last_voice_time > SILENCE_THRESHOLD:
                    print("Pausa detectada, guardando archivo...")
                    save_recording(frames, start_time)
                    reset_recording()
            if time.time() - last_voice_time > NO_VOICE_TIMEOUT:
                print("No se detectó voz en 10 segundos, finalizando...")
                break

    except KeyboardInterrupt:
        print("Grabación detenida por el usuario.")

    if recording:
        save_recording(frames, start_time)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    print("Programa finalizado.")

if __name__ == '__main__':
    main()
