###################################################################################
##
# Author:      gatito
#
# Created:     18/Jul/2024
# Copyright:   (c) gatito 2024 en postPandemia, antes de crisis Mexico
# Licence:     Licence MIT

# -------------------------------------------------------------------------------
# conda create --name whisperenv python=3.10
#
# La intencion de esta rutinas es que siempre esten ejecutandose
# Para escuchar y dejarlo / escucha, y convertir audio a texto dejarlo en carpeta /conversa
# Para cuando exista un texto en leer, convertirlo en .mp3 y dejarlo en acento_local
# decirlo en audio y moverlo a leido
# Función para convertir audio a texto usando Whisper
# Función para monitorear la carpeta "leer" y convertir texto a audio dejar en /conversa
# Función para mostrar el texto en pantalla

import os
import threading
import time
from datetime import datetime
import whisper
from glob import glob

# Inicializar el modelo Whisper
model = whisper.load_model("base")

# Carpeta donde se guardan los audios convertidos a texto
OUTPUT_DIR = "escucha/"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Carpeta donde se monitorizan los archivos para convertir a audio
READ_DIR = "leer/"

CONVERSA_DIR = "conversa/"
os.makedirs(CONVERSA_DIR, exist_ok=True)

# Variable global para almacenar el texto detectado
detected_text = ""
text_lock = threading.Lock()

# Función para convertir audio a texto usando Whisper
def listen_and_convert():
    global detected_text
    while True:
        # Obtener la fecha y hora actual en formato YYYYMMDDHHMMSS
        fecha_hora = datetime.now().strftime("%Y%m%d%H%M%S")
        # Simular la escucha continua (en un entorno real, captura el audio)
        # audio_file = ("mic_audio.mp3")
        audio_file = os.path.join(OUTPUT_DIR, f"{fecha_hora}_audio.mp3")
        if os.path.exists(audio_file):
            # Convertir audio a texto usando Whisper
            result = model.transcribe(audio_file)
            text = result['text']
            with text_lock:
                detected_text += text + " "
            # Guardar el texto en la carpeta 'escucha'
            with open(os.path.join(CONVERSA_DIR, f"{fecha_hora}_audio.txt"), "w") as f:
                f.write(text)
            # os.remove(audio_file)
        time.sleep(1)  # Simular espera de 1 segundo para la siguiente captura
        print("Escuche")

# Función para monitorear la carpeta "leer" y convertir texto a audio
def monitor_and_speak():
    while True:
        files = glob(os.path.join(READ_DIR, "*.txt"))
        if files:
            for file in files:
                with open(file, "r") as f:
                    text = f.read()
                # Convertir texto a audio
                output_audio = os.path.join(READ_DIR, f"audio_{time.time()}.mp3")
                command = f"whisper {text} --model base --output {output_audio}"
                os.system(command)
                # Reproducir el audio y mostrar la animación
                # playsound(output_audio)
                # Mostrar animación en pantalla (se puede personalizar más)
                print(" " * 20 + text)
                os.remove(file)
        time.sleep(2)  # Verificar cada 2 segundos

# Función para mostrar el texto en pantalla
def display_text():
    global detected_text
    while True:
        with text_lock:
            print(detected_text[-80:].rjust(80))  # Muestra las últimas 2 filas del texto
            if detected_text and len(detected_text) > 160:
                detected_text = detected_text[-160:]  # Mantén solo las últimas 2 filas de texto
        time.sleep(0.1)  # Actualiza la pantalla cada 100 ms

if __name__ == '__main__':
    # Iniciar las rutinas en hilos separados
    threading.Thread(target=listen_and_convert, daemon=True).start()
    # threading.Thread(target=monitor_and_speak, daemon=True).start()
    # threading.Thread(target=display_text, daemon=True).start()
    print("Termino")