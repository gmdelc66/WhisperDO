###################################################################################
##
# Author:      gatito
#
# Created:     1/sep/2024
# Copyright:   (c) gatito 2024 en postPandemia, antes de crisis Mexico
# Licence:     Licence MIT
###################################################################################
# Busca los dispositivos de audio validos intenta hacer grabacion, para ver si son
# funcionales y crea archivo donde se guardan los dispositivos validos
# despues pide al usuario dicte un texto
# para ver
# cual de los dispositivos y de las configuraciones tiene la mejor
# Transcripcion
##################################################################################
#
# Explicación del Código:
#
#     Verificación de dispositivos:
#         Se intenta abrir cada dispositivo con 1 y 2 canales. Si tiene éxito,
#         se agrega a VALID_DEVICES.
#     Formato (FORMAT): Define el formato de los datos de audio (en este caso, paInt16, que es un formato de 16 bits).
#     Canales (CHANNELS_OPTIONS): Prueba con 1 y 2 canales para ver cuál ofrece la mejor transcripción.
#     Chunk (CHUNK): Define el tamaño de los bloques de datos que se procesan en cada iteración de grabación.
#     Duración (DURATION): La duración de la grabación en segundos.
#     Comparación: Usa la biblioteca difflib para comparar el texto original con el transcrito y encontrar la mejor coincidencia.
#     Limpieza de Pantalla: Cada vez que se inicia una prueba,
#     se limpia la pantalla y se muestra el texto a dictar.
# #
#     Prueba de transcripción:
#         Solo se prueban los dispositivos y canales que pasaron la verificación anterior.
#         Se muestra el texto en varias líneas en la consola para que el usuario lo lea.
#         Se graba el audio y se transcribe usando Whisper.
#         Se guarda tanto el archivo de audio como la transcripción y se compara con el texto original.
#         El código imprime los resultados en pantalla.
#
# Manejo de errores:
#
#     Si algún dispositivo o canal falla durante la grabación o transcripción,
#     el programa continúa con el siguiente dispositivo o canal válido.
#
# Ejecución:
#
#     El programa recorrerá cada dispositivo y grabará el texto utilizando 1 y 2 canales.
#     Después de la grabación, transcribirá el audio y comparará la transcripción con el
#     texto original.
#     Al final, se mostrará la mejor configuración de dispositivo y canales basada en la
#     coincidencia de texto.

import pyaudio
import wave
import os
import whisper
import json
import difflib
from audio_fix import preprocess_audio

# Parámetros de grabación
FORMAT = pyaudio.paInt16
CHANNELS_LIST = [1, 2]  # Se prueban 1 y 2 canales
RATE = 44100  # Frecuencia de muestreo, puede usarse 48000 aunque whisper no funciona mejor
CHUNK = 1024
DURATION = 15  # Duración de la grabación en segundos
TEXT = (
    "Por favor en microfono lee el siguiente texto:\n"
    "La mamá del rápido zorro marrón salta sobre el perezoso perro que no toma mama,\n"
    "mientras la lluvia cae en el jardín exuberante. Y el zumo está muy frío."
)
# Aqui guardamos pruebas de microfono y transcripcion de prueba
OUTPUT_DIR = "mic_test/" # En esta carpeta van a estar config
os.makedirs(OUTPUT_DIR, exist_ok=True) # No existe creala
# Aqui guardamos configuracion de dispositivos encontrados y acuracy de cada uno
CONFIG_DIR = "config/" # En esta carpeta van a estar config
os.makedirs(CONFIG_DIR, exist_ok=True) # No existe creala

CONFIG_FILE = os.path.join(CONFIG_DIR, "config_valido.json") # Archivo para almacenar dispositivos válidos

def check_device(audio, device_index, channels, rate=RATE, duration=2):
    try:
        # Abrir el stream con los parámetros especificados
        stream = audio.open(
            format=FORMAT,
            channels=channels,
            rate=rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=2048  # Tamaño del buffer ajustado
        )

        # Intentar grabar un pequeño fragmento para verificar si el dispositivo funciona
        stream.start_stream()
        frames = []
        for _ in range(int(rate / 2048 * duration)):  # Graba por la duración especificada
            data = stream.read(2048, exception_on_overflow=False)  # Añadido manejo de excepción para desbordamiento
            frames.append(data)

        # Detener y cerrar el stream
        stream.stop_stream()
        stream.close()

        # Verificar si se grabó algo significativo
        if frames:
            return True
        else:
            print(f"Dispositivo {device_index} con {channels} canales no produjo audio válido.")
            return False

    except IOError as e:
        print(f"Error de I/O en dispositivo {device_index} con {channels} canales: {e}")
        return False
    except pyaudio.paBadIODeviceCombination as e:
        print(f"Error de PyAudio en dispositivo {device_index} con {channels} canales: {e}")
        return False
    except Exception as e:
        print(f"Error general en dispositivo {device_index} con {channels} canales: {e}")
        return False

def record_and_transcribe(audio, device_index, channels):
    filename= os.path.join(OUTPUT_DIR, f"test_device_{device_index}_channels_{channels}.wav")
    print("Escuchando Audio...")
    try:
        stream = audio.open(format=FORMAT, channels=channels, rate=RATE, input=True, input_device_index=device_index,
                            frames_per_buffer=CHUNK)
        frames = []
        for _ in range(0, int(RATE / CHUNK * DURATION)):
            data = stream.read(CHUNK)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        print("Grabando Audio...")
        # Guardar el archivo de audio
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        print("Transcribiendo texto...")
        # Transcribir el archivo de audio usando Whisper
        model = whisper.load_model("large-v3")  # Asegúrate de tener el modelo correcto instalado
        result = model.transcribe(filename)

        # Guardar la transcripción
        with open(f"{filename}.txt", "w") as f:
            f.write(result["text"])
        print("Texto transcrito")
        print(result["text"])

        # Comparar la transcripción con el texto original
        accuracy = compare_texts(result["text"], TEXT)
        print(f"Transcripción con una precisión del {accuracy:.2f}%")
        # Aplicar preprocesamiento de audio
        preprocessed_filename = preprocess_audio(filename)
        # model = whisper.load_model("base")  # Asegúrate de tener el modelo correcto instalado
        """        
        result = model.transcribe(filename)
        # Guardar la transcripción

        with open(f"{filename}_fix.txt", "w") as f:
            f.write(result["text"])
        print("Texto transcrito con fix")
        print(result["text"])

        # Comparar la transcripción con el texto original
        accuracy_fix = compare_texts(result["text"], TEXT)
        print(f"Transcripción con una precisión del {accuracy_fix:.2f}%")
        if accuracy_fix > accuracy: #Correccion de audio funciono
            accuracy = accuracy_fix
            filename = f"{filename}_fix.txt"
        """
        return accuracy, filename

    except Exception as e:
        print(f"Error al grabar o transcribir en dispositivo {device_index} con {channels} canales: {e}")
        return 0, filename

def compare_texts(transcribed_text, original_text):
    # Explicación:
    #
    #     difflib.SequenceMatcher: Compara dos secuencias y retorna una medida de
    #     similitud entre 0 y 1, donde 1 indica que las secuencias son idénticas.
    #     ratio(): Retorna la similitud como un valor flotante entre 0 y 1.
    #     similarity_percentage: Multiplicamos la ratio por 100 para obtener un
    #     porcentaje.

    # Limpiar y dividir los textos en palabras
    transcribed_words = transcribed_text.strip().lower().split()
    original_words = original_text.strip().lower().split()

    # Utilizar difflib para calcular una similitud de secuencia
    matcher = difflib.SequenceMatcher(None, original_words, transcribed_words)
    similarity = matcher.ratio()  # Retorna un valor entre 0 y 1

    # Convertir la similitud a un porcentaje
    similarity_percentage = similarity * 100
    return similarity_percentage

def load_valid_devices(audio):
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            devices = json.load(file)
            if devices:
                print("Encontre archivos de dispositivos valido, voy a usar estos")
                return devices

    # Si no hay archivo o no tiene dispositivos válidos, obtener todos los dispositivos del sistema
    all_devices = []
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        all_devices.append({
            'device_info': (i, 1),  # Supone 1 canal por defecto
            'channels_list': CHANNELS_LIST  # Canales a probar
        })
    print("No encontre lista de dispositivos, voy a probar todos los del equipo")
    return all_devices


def save_valid_devices(devices):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(devices, f)

def main():
    audio = pyaudio.PyAudio()

    # Cargar dispositivos válidos o todos los dispositivos si no hay configuración previa
    valid_devices = load_valid_devices(audio)
    valid_device_indices = {tuple(dev['device_info']): False for dev in valid_devices}

    # Verificación de dispositivos válidos
    for device in valid_devices:
        device_index, _ = device['device_info']
        for channels in device.get('channels_list', CHANNELS_LIST):
            if check_device(audio, device_index, channels):
                valid_device_indices[(device_index, channels)] = True
            else:
                print(f"Dispositivo {device_index} falló con {channels} canales.")

    print(f"Dispositivos válidos después de la verificación inicial: {valid_device_indices}")

    # Prueba de grabación y transcripción solo en dispositivos válidos
    valid_transcription_devices = []
    for (device_index, channels), is_valid in valid_device_indices.items():
        if not is_valid:
            continue

        os.system('clear')
        print(f"Dispositivo: {audio.get_device_info_by_index(device_index)['name']}, Index: {device_index}, Canales: {channels}")
        print(TEXT)
        input("Cuando estés listo, presiona cualquier tecla para comenzar la grabación...")

        accuracy, filename = record_and_transcribe(audio, device_index, channels)
        if accuracy > 0:
            # print(f"Transcripción exitosa para {filename} con una precisión del {accuracy:.2f}%")
            # Guardar información del dispositivo junto con la precisión
            valid_transcription_devices.append({
                'device_info': (device_index, channels),
                'format': FORMAT,
                'rate': RATE,
                'chunk': CHUNK,
                'duration': DURATION,
                'accuracy': accuracy
            })
        else:
            print(f"Transcripción fallida para {filename}")
            valid_device_indices[(device_index, channels)] = False

    # Guardar los dispositivos válidos después de la prueba de transcripción
    if valid_transcription_devices:
        save_valid_devices(valid_transcription_devices)

    audio.terminate()

if __name__ == "__main__":
    main()
