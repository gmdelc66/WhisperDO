#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
# para optimizar whisper
# sudo apt install libopenblas-dev liblapack-dev
# nano .bashrc
# export BLAS=openblas
# export LAPACK=openblas
# source ~/.bashrc # para cargar variables
# echo $BLAS
# echo $LAPACK
# conda install openblas
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
import numpy as np
import time

from icecream import ic

from spyder.plugins.completion.providers.snippets.widgets.snippetsconfig import LANGUAGE

# Rutinas de utilerias de Gatito
from audio_fix import preprocess_audio
from temporizador import Timer
from utils import limpiar_texto
# Crear una instancia del Timer
timer = Timer()

# Parámetros de grabación
FORMAT = pyaudio.paInt16
# CHANNELS_LIST = [1, 2]  # Se prueban 1 y 2 canales
CHANNELS_LIST = [1]  # solo 2do canal
# RATE = 44100  # Frecuencia de muestreo, puede usarse 48000 aunque
              # whisper no funciona mejor
RATE = 16000 # frecuencia para DeepSpeech
CHUNK = 1024
DURATION = 15  # Duración de la grabación en segundos
NOISE_THRESHOLD = 20  # Umbral de ruido en dB
NOISE_DURATION = 2  # Duración del umbral de ruido en segundos

MODEL_NAME = "large-v3"
# Modelos disponibles 5/sep/2024 ['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large']
LANGUAGE = "spanish"
# RATE = 48000
# MODEL_NAME = "large"spanish, Index 7, Channel 2, precision 72.73%, Tiempo 53 segundos:418 milisegundos

# RATE = 16000
# MODEL_NAME = "tiny"spanish, Index 6, Channel 2, precision 48.48%, Tiempo 04 segundos :295 milisegundos
# MODEL_NAME = "base"spanish, Index 6, Channel 2, precision 63.64%, Tiempo 07 segundos:313 milisegundos
# MODEL_NAME = "small"spanish, Index 6, Channel 2, precision 67.69%, Tiempo 20 segundos:619 milisegundos
# MODEL_NAME = "medium"spanish, Index 6, Channel 2, precision 78.79%, Tiempo 01 minutos:05 segundos:611 milisegundos
# MODEL_NAME = "large-v1"spanish, Index 6, Channel 2, precision 81.82%, Tiempo 04 minutos:22 segundos:237 milisegundos
# MODEL_NAME = "large-v1"spanish, Index 7, Channel 2, precision 75.76%, Tiempo 01 minutos:38 segundos:219 milisegundos
# MODEL_NAME = "large-v1"spanish, Index 7, Channel 1, precision 78.79%, Tiempo 51 segundos:093 milisegundos
# MODEL_NAME = "large-v2"spanish, Index 7, Channel 1, precision 72.73%, Tiempo 50 segundos:892 milisegundos
# MODEL_NAME = "large-v2"spanish, Index 7, Channel 2, precision 78.79%, Tiempo 51 segundos:087 milisegundos
# MODEL_NAME = "large-v3"spanish, Index 7, Channel 1, precision 76.53%, Tiempo 01 minutos:04 segundos:100 milisegundos
# MODEL_NAME = "large-v3"spanish, Index 7, Channel 2, precision 78.79%, Tiempo 48 segundos:431 milisegundos
# MODEL_NAME = "large"spanish, Index 7, Channel 1, precision 78.79%, Tiempo 54 segundos:529 milisegundos
# MODEL_NAME = "large"spanish, Index 7, Channel 2, precision 76.72%, Tiempo 49 segundos:406 milisegundos
# La transcripcion esta bien solo puntuacion incorrecta

# *** Estos son parametros para mejor solo errores puntuacion
# Transcripción limpia con una precisión del 100.00%'
# RATE = 16000 # frecuencia para DeepSpeech
# CHUNK = 1024
# DURATION = 0  # Duración de la grabación en segundos
# NOISE_THRESHOLD = 20  # Umbral de ruido en dB
# NOISE_DURATION = 2  # Duración del umbral de ruido en segundos
# **** MODEL_NAME = "large-v3"spanish, Index 7, Channel 1, precision 86.21%, Tiempo 51 segundos:665 milisegundos

TEXTshow = (
    "Por favor en microfono lee el siguiente texto:\n"
    "La mamá del rápido zorro marrón salta sobre el perezoso perro que no toma mama,\n"
    "mientras la lluvia cae en el jardín exuberante. Y el zumo está muy frío."
)
TEXT = (
    "La mamá del rápido zorro marrón salta sobre el perezoso perro que no toma mama,\n"
    "mientras la lluvia cae en el jardín exuberante. Y el zumo está muy frío."
)
TEXTENG = ("The quick brown fox's mom jumps over the lazy dog who doesn't take milk, \n"
        "while the rain falls in the lush garden. And the juice is very cold.")
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

# Function to detect leading silence
# Returns the number of milliseconds until the first sound (chunk averaging more than X decibels)
def milliseconds_until_sound(sound, silence_threshold_in_decibels=-20.0, chunk_size=10):
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold_in_decibels and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms

# At times, files with long silences at the beginning can cause Whisper
# to transcribe the audio incorrectly. We'll use Pydub to detect
# and trim the silence.
def trim_start(filepath):
    from pathlib import Path
    from pydub import AudioSegment
    path = Path(filepath)
    directory = path.parent
    filename = path.name
    audio = AudioSegment.from_file(filepath, format="wav")
    start_trim = milliseconds_until_sound(audio)
    trimmed = audio[start_trim:]
    new_filename = directory / f"trimmed_{filename}"
    trimmed.export(new_filename, format="wav")
    return trimmed, new_filename

def calculate_noise_level(data, sample_width):
    # Función calculate_noise_level: Esta función convierte los datos de
    # audio en un array de NumPy y calcula el nivel de ruido en dB.
    # Convertir los datos de audio a un array de numpy
    audio_data = np.frombuffer(data, dtype=np.int16)
    # Calcular el nivel de ruido en dB
    rms = np.sqrt(np.mean(audio_data**2))
    if rms > 0:
        noise_level = 20 * np.log10(rms)
    else:
        noise_level = -float('inf')  # En caso de RMS = 0, el nivel de ruido es infinitamente bajo
    ic(noise_level)
    return noise_level


def record_audio(filename, audio, device_index, channels, duration):
    ic(("Escuchando Audio..."))
    try:
        stream = audio.open(
            format=FORMAT,
            channels=channels,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
        frames = []
        if duration > 0:
            # Grabación con duración fija
            for _ in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
        else:
            # Grabación sin duración fija, detectando el ruido
            silence_start = None
            while True:
                data = stream.read(CHUNK)
                noise_level = calculate_noise_level(data, audio.get_sample_size(FORMAT))
                frames.append(data)

                # Si el nivel de ruido es bajo, iniciar temporizador
                if noise_level < NOISE_THRESHOLD:
                    ic(f"Voy a terminar grabación en: {NOISE_DURATION}")
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start > NOISE_DURATION:
                        break  # Terminamos la grabación si el ruido es bajo durante NOISE_DURATION
                else:
                    silence_start = None  # Reseteamos el temporizador si hay ruido

        stream.stop_stream()
        stream.close()

        # Guardar el archivo de audio
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        ic("Audio Grabado...")
        return filename  # Regresa el archivo creado
    except Exception as e:
        print(f"Error: {e}")


def record_and_transcribe(filename, audio, device_index, channels):
    # filename = os.path.join(OUTPUT_DIR, f"test_device_{device_index}_channels_{channels}.wav")
    try:
        record_audio(filename, audio, device_index, channels, DURATION) # Graba el audio de microfono
        # filename = trim_start(filename) # Corta los silencios iniciales
        ic("Transcribiendo texto...")
        timer.start() #Inicializa Temporizador
        # Transcribir el archivo de audio usando Whisper
        # Cargar el modelo de Whisper
        model = whisper.load_model(MODEL_NAME)  # Asegúrate de tener el modelo correcto instalado

        # Mostrar los parámetros utilizados
        result = model.transcribe(filename, language=LANGUAGE,temperature=0)

        # Verificar si 'text' está en el resultado de la transcripción
        if 'text' in result:
            transcribed_text = result['text']
            ic("Texto transcrito")
            print(transcribed_text)

            # Guardar la transcripción
            with open(f"{filename}.txt", "w") as f:
                f.write(transcribed_text)

            # Comparar la transcripción con el texto original
            accuracy, limpio_porc = compare_texts(transcribed_text, TEXT)
            ic(f"Transcripción con una precisión del {accuracy:.2f}%")
            ic(f"Transcripción limpia con una precisión del {limpio_porc:.2f}%")
            """            # Aplicar preprocesamiento de audio
            preprocessed_filename = preprocess_audio(filename)
            # Volver a transcribir el audio preprocesado
            result = model.transcribe(preprocessed_filename)

            if 'text' in result:
                transcribed_text_fix = result['text']
                print("Texto transcrito con fix")
                print(transcribed_text_fix)

                # Guardar la transcripción corregida
                with open(f"{preprocessed_filename}_fix.txt", "w") as f:
                    f.write(transcribed_text_fix)

                # Comparar la transcripción corregida con el texto original
                accuracy_fix = compare_texts(transcribed_text_fix, TEXT)
                print(f"Transcripción con una precisión del {accuracy_fix:.2f}%")
                if accuracy_fix > accuracy:  # Corrección de audio funcionó
                    accuracy = accuracy_fix
                    filename = f"{preprocessed_filename}_fix.txt"
            """
        else:
            print("No se detectó texto en el fragmento de audio.")
            accuracy = 0

        return transcribed_text, accuracy

    except Exception as e:
        print(f"Error al transcribir texto  {filename}: {e}")
        return 0

def compare_texts(transcribed_text, original_text):
    # Explicación:
    #
    #     difflib.SequenceMatcher: Compara dos secuencias y retorna una medida de
    #     similitud entre 0 y 1, donde 1 indica que las secuencias son idénticas.
    #     ratio(): Retorna la similitud como un valor flotante entre 0 y 1.
    #     similarity_percentage: Multiplicamos la ratio por 100 para obtener un
    #     porcentaje.

    # dividir los textos en palabras
    transcribed_words = transcribed_text.strip().split()
    original_words = original_text.strip().split()

    # Utilizar difflib para calcular una similitud de secuencia
    matcher = difflib.SequenceMatcher(None, original_words, transcribed_words)
    similarity = matcher.ratio()  # Retorna un valor entre 0 y 1

    # Convertir la similitud a un porcentaje
    similarity_percentage = similarity * 100

    # verificar limpiando texto, de puntuacion, acentos y signos
    # Separa en palabras
    original_limpio = limpiar_texto(original_text).strip().split()
    transcrito_limpio = limpiar_texto(transcribed_text).strip().split()
    matcher = difflib.SequenceMatcher(None, original_limpio, transcrito_limpio)
    similarity = matcher.ratio()  # Retorna un valor entre 0 y 1
    similarity_limpio = similarity * 100
    return similarity_percentage, similarity_limpio

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
    ic(f"Modelos existentes en whisper: {whisper.available_models()}") # muestra todos los modelos existentes
    # Verificación de dispositivos válidos
    for device in valid_devices:
        device_index, _ = device['device_info']
        for channels in device.get('channels_list', CHANNELS_LIST):
            if check_device(audio, device_index, channels):
                valid_device_indices[(device_index, channels)] = True
            else:
                print(f"Dispositivo {device_index} falló con {channels} canales.")

    ic(f"Dispositivos válidos después de la verificación inicial: {valid_device_indices}")

    # Prueba de grabación y transcripción solo en dispositivos válidos
    valid_transcription_devices = []
    for (device_index, channels), is_valid in valid_device_indices.items():
        if not is_valid:
            continue
        DURATION = 0
        ic(DURATION)
        os.system('clear')
        ic(f"Dispositivo: {audio.get_device_info_by_index(device_index)['name']}, Index: {device_index}, Canales: {channels}")
        print(TEXTshow)
        # timer.elapsed() #Inicia tiempo de ejecucion
        input("Cuando estés listo, presiona cualquier tecla para comenzar la grabación...")
        filename = os.path.join(OUTPUT_DIR, f"test_device_{device_index}_channels_{channels}.wav")
        transcribed_text, accuracy = record_and_transcribe(filename, audio, device_index, channels) # Graba y transcribe
        ic(f"Modelo utilizado: {MODEL_NAME}")
        ic(f"Idioma seleccionado: {LANGUAGE}")
        # Consultar el tiempo transcurrido
        timer.elapsed() # Termina el tiempo de ejecucion
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

