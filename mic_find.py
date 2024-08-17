# Explicación:
#
#     Listar Dispositivos: La función list_audio_devices lista todos los
#     dispositivos de audio disponibles en tu equipo junto con detalles como el
#     número de canales, la tasa de muestreo y la latencia.
#
#     Seleccionar el Mejor Dispositivo: La función find_best_input_device recorre
#     todos los dispositivos de entrada y selecciona el que tenga el mayor número de
#     canales de entrada.

import os
import pyaudio
import wave
import time

# Configuración de la grabación
FORMAT = pyaudio.paInt16
CHANNELS = 1
CHUNK = 1024
DURATION = 10 # Duración de la grabación en segundos

# Directorio de salida
OUTPUT_DIR = "mic_tests/"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def record_device(audio, device_index, device_name):
    """Graba audio desde un dispositivo específico y guarda el archivo."""
    try:
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=16000,  # Ajusta según la tasa de muestreo soportada
                            input=True,
                            input_device_index=device_index,
                            frames_per_buffer=CHUNK)
        print(f"Grabando desde {device_name} (ID: {device_index})")

        frames = []
        for _ in range(0, int(16000 / CHUNK * DURATION)):
            data = stream.read(CHUNK)
            frames.append(data)

        # Detener y cerrar el flujo
        stream.stop_stream()
        stream.close()

        # Guardar archivo WAV
        filename = f"device_{device_index}.wav"
        file_path = os.path.join(OUTPUT_DIR, filename)
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(16000)
            wf.writeframes(b''.join(frames))

        print(f"Archivo guardado como {file_path}")

    except Exception as e:
        print(f"Error al grabar desde {device_name} (ID: {device_index}): {e}")


def list_and_test_devices():
    """Lista todos los dispositivos de audio disponibles y prueba la grabación con cada uno."""
    audio = pyaudio.PyAudio()
    devices = []

    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        device_name = device_info['name']
        print(f"Dispositivo: {device_name} (ID: {i})")

        # Intentar grabar desde el dispositivo
        record_device(audio, i, device_name)

    audio.terminate()


if __name__ == "__main__":
    list_and_test_devices()
