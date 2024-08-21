# crear múltiples archivos cuando se detecta voz.
# El programa creará un nuevo archivo si hay una pausa mayor a un número determinado de segundos o
# si el usuario dice "point".
# Los archivos estarán nombrados con el formato yyyymmddhhmmss, correspondiente a la fecha y hora
# de inicio de cada grabación:

import pyaudio
import wave
import speech_recognition as sr
import time
import datetime

# Configuración para la grabación
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
SILENCE_THRESHOLD = 2  # Número de segundos de silencio para crear un nuevo archivo
KEYWORD = "point"  # Palabra clave para iniciar un nuevo archivo

# Inicializa PyAudio
audio = pyaudio.PyAudio()

# Inicia la grabación
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

print("Escuchando...")

frames = []
recording = False
last_voice_time = None
file_index = 1

# Inicializa el reconocedor de voz
recognizer = sr.Recognizer()


def save_recording(frames, start_time):
    """Guarda la grabación en un archivo WAV con un nombre basado en la fecha y hora."""
    if not frames:
        return
    filename = f"{start_time.strftime('%Y%m%d%H%M%S')}.wav"
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print(f"Grabación guardada en {filename}")


def reset_recording():
    """Resetea los datos de la grabación."""
    global frames, recording, last_voice_time
    frames = []
    recording = False
    last_voice_time = None


try:
    while True:
        # Lee un bloque de datos de audio
        data = stream.read(CHUNK)
        frames.append(data)

        # Convierte el bloque de datos a formato adecuado para el reconocedor
        audio_data = sr.AudioData(data, RATE, audio.get_sample_size(FORMAT))

        # Detección de voz
        try:
            transcription = recognizer.recognize_google(audio_data, show_all=False).lower()
            print(f"Transcripción detectada: {transcription}")

            if KEYWORD in transcription:
                print("Palabra clave detectada, creando nuevo archivo...")
                save_recording(frames, start_time)
                reset_recording()
                continue

            if not recording:
                print("Voz detectada, iniciando grabación...")
                recording = True
                start_time = datetime.datetime.now()
                last_voice_time = time.time()

            else:
                last_voice_time = time.time()

        except sr.UnknownValueError:
            pass  # No se detectó voz en este bloque

        # Verifica si ha pasado suficiente tiempo de silencio para iniciar un nuevo archivo
        if recording and (time.time() - last_voice_time) > SILENCE_THRESHOLD:
            print("Pausa larga detectada, creando nuevo archivo...")
            save_recording(frames, start_time)
            reset_recording()

except KeyboardInterrupt:
    print("Grabación detenida por el usuario.")

# Finaliza la grabación si está en progreso
if recording:
    save_recording(frames, start_time)

# Limpia y cierra el stream
stream.stop_stream()
stream.close()
audio.terminate()

print("Programa finalizado.")
