# Explicación del código:
#
#     Hilo de captura de audio (capture_audio):
#         Captura el audio desde el micrófono usando sounddevice.
#         Cada fragmento de audio (durante block_duration segundos) se coloca
#         en una cola (audio_queue) para ser procesado.
#
#     Hilo de transcripción (transcribe_audio):
#         Revisa continuamente si hay fragmentos de audio en la cola.
#         Si hay audio disponible, lo transcribe usando el modelo de stable_whisper
#         y muestra el texto resultante.
#
#     Uso de hilos:
#         Dos hilos (o threads) corren en paralelo: uno para capturar el audio y otro
#         para transcribirlo. Esto permite capturar y procesar el audio de forma simultánea.
#
#     Cola:
#         El audio capturado se almacena en la cola, lo que permite que los fragmentos
#         de audio sean procesados de manera asíncrona por el hilo que transcribe el audio.
# INSTALL
# sudo apt update && sudo apt install ffmpeg
# pip install -U stable-ts
# pip install stable-whisper sounddevice numpy

import sounddevice as sd
import numpy as np
import stable_whisper as whisper
import queue
import threading

# Definir parámetros del audio
samplerate = 16000  # Tasa de muestreo
block_duration = 3  # Duración del bloque de audio en segundos
audio_queue = queue.Queue()  # Cola para almacenar los fragmentos de audio

# Cargar el modelo de stable_whisper
model = whisper.load_model('small')

# Hilo que captura audio y lo pone en la cola
def capture_audio():
    def audio_callback(indata, frames, time, status):
        if status:
            print(f"Estado del micrófono: {status}")
        audio_data = np.squeeze(indata)  # Aplanar el array de audio
        audio_queue.put(audio_data)  # Colocar los fragmentos de audio en la cola

    # Iniciar la grabación del micrófono
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=samplerate, blocksize=int(samplerate * block_duration)):
        print("Grabando audio... Presiona Ctrl+C para detener.")
        while True:
            sd.sleep(1000)  # Mantener la captura de audio activa

# Hilo que procesa el audio y lo transcribe
import sounddevice as sd


def transcribe_audio():
    while True:
        if not audio_queue.empty():
            audio_data = audio_queue.get()  # Obtener fragmento de audio de la cola

            # Reproducir el fragmento de audio para escucharlo
            sd.play(audio_data, samplerate=samplerate)
            sd.wait()  # Esperar a que termine la reproducción del audio

            # Transcribir el audio
            result = model.transcribe(audio_data, fp16=False, language="spanish")

            # Verificar si hay segmentos en la transcripción
            if 'segments' in result and result['segments']:
                for segment in result['segments']:  # Iterar sobre los segmentos de audio
                    print(f"Transcripción: {segment['text']}")  # Mostrar el texto de cada segmento
            else:
                print(".../n")

def main():
    # Crear los hilos
    audio_thread = threading.Thread(target=capture_audio)
    transcription_thread = threading.Thread(target=transcribe_audio)

    # Iniciar los hilos
    audio_thread.start()
    transcription_thread.start()

    # Unir los hilos al hilo principal para que corran continuamente
    audio_thread.join()
    transcription_thread.join()

if __name__ == "__main__":
    main()
