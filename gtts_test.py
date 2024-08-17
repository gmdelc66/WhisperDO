###################################################################################
##
# Author:      gmdelc@gmail.com
#
# Created:     24/ago/2024
# Copyright:   (c) gatito 2024 en postPandemia, antes de crisis Mexico
# Licence:     Licence MIT

# -------------------------------------------------------------------------------
#
# Descripción del Script, Script para Generar audio desde texto y crear Archivos
# de Audio con # Diferentes TLDs (acentos locales)
#
# Resumen puedes ejecutar python gtts_test.py "quiero oir esto"
#       o importar y llamar  main("quiero oir esto") desde otra rutina
#
#     Luego, en otro archivo (caller.py), importa la función main y pásale el texto que quieras.
#
#     Con estos pasos, podrás ejecutar caller.py, que llamará a main() con el texto "este texto como parametro" en lugar del texto predeterminado o el texto proporcionado desde la línea de comandos.
#   Los parametros de voz que escuche mas cercanos al español de mexico son:
#   lang="es",tld="ca"
# Las rutinas dentro de esto
#
#   Uso crea_reproduce(text)
#
#     Lista de Locales: La lista de acentos locales códigos de idioma, TLDs y descripciones para cada variante local que has proporcionado.
#
#       Directorio donde se guardarán los archivos
#       directorio = "acento_local" si no existe se creara
#   Texto que se convertirá en voz
#     Se puede solo generar un archivo con un idioma y acento o con cada unos de los miembros de la lista,
#     para ver cual nos funciona mejor
#     Generación de Archivos: Para cada combinación de idioma y TLD en la lista, el script genera un archivo
#     de audio.
#       Obtención de la Fecha y Hora: Usamos datetime.now().strftime("%Y%m%d%H%M%S") para obtener la fecha
#       y hora actual en el formato YYYYMMDDHHMMSS.

#     Nombre del Archivo: El nombre del archivo se genera con la marca de tiempo incluida al principio del
#     nombre, ({fecha_hora}_audio_{lang}_{tld}.mp3).
#     Reproducción de Archivos: se usa idioma es, local com.mx o es ca velocidad 1.58, y tono .54, son los
#     mas parecidos a nuestros español)
#     Después de guardar cada archivo, el script lo reproduce y muestra en pantalla el nombre del archivo
#     y su descripción.
#
#     Manejo de Errores: El script captura y muestra errores si ocurre algún problema al guardar o
#     reproducir los archivos.#
##############################################################################################################
from gtts import gTTS
import os
import subprocess
from datetime import datetime
import argparse

from mypy.dmypy.client import help_parser

# Lista de TLDs para diferentes acentos y locales
locales = [
    ('en', 'com.au', 'English (Australia)'),
    ('en', 'co.uk', 'English (United Kingdom)'),
    ('en', 'us', 'English (United States)'),
    ('en', 'ca', 'English (Canada)'),
    ('en', 'co.in', 'English (India)'),
    ('en', 'ie', 'English (Ireland)'),
    ('en', 'co.za', 'English (South Africa)'),
    ('en', 'com.ng', 'English (Nigeria)'),
    ('fr', 'ca', 'French (Canada)'),
    ('fr', 'fr', 'French (France)'),
    ('zh-CN', 'any', 'Mandarin (China Mainland)'),
    ('zh-TW', 'any', 'Mandarin (Taiwan)'),
    ('pt', 'com.br', 'Portuguese (Brazil)'),
    ('pt', 'pt', 'Portuguese (Portugal)'),
    ('es', 'com.mx', 'Spanish (Mexico)'),
    ('es', 'es', 'Spanish (Spain)'),
    ('es', 'us', 'Spanish (United States)')
]

# Directorio donde se guardarán los archivos
directorio = "acento_local"
os.makedirs(directorio, exist_ok=True)
# Texto que se convertirá en voz


# Reproductor de audio con ajustes en tiempo real
def reproducir_audio(archivo, velocidad=1.0, tono=1.0):
    try:
        print(f"Reproduciendo: {archivo} (Velocidad: {velocidad}, Tono: {tono})")
        cmd = [
            "ffplay", "-nodisp", "-autoexit",
            "-af", f"atempo={velocidad},asetrate=44100*{tono},aresample=44100",
            archivo
        ]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al reproducir el archivo {archivo}. Error: {e}")

def genera_muestra_acentos(text, lang="es",tld="ca"):
    # Obtener la fecha y hora actual en formato YYYYMMDDHHMMSS
    fecha_hora = datetime.now().strftime("%Y%m%d%H%M%S")
    if lang != "all":
        # Crear objeto gTTS
        tts = gTTS(text=text, lang=lang, slow=False, tld=tld)

        # Nombre del archivo con marca de tiempo
        archivo_audio = os.path.join(directorio, f"{fecha_hora}_audio_{lang}_{tld}.mp3")

        # Guardar el archivo de audio
        tts.save(archivo_audio)
        print(f"Archivo guardado: {archivo_audio}")
        return archivo_audio # Regresa nombre del archivo
    else: # Puso all, haste archivo con todos los idiomas
        for lang, tld, descripcion in locales:
            try:
                # Crear objeto gTTS
                tts = gTTS(text=text, lang="es", slow=False, tld=tld)

                # Nombre del archivo con marca de tiempo
                archivo_audio = os.path.join(directorio, f"{fecha_hora}_audio_{lang}_{tld}.mp3")

                # Guardar el archivo de audio
                tts.save(archivo_audio)
                print(f"Archivo guardado: {archivo_audio} ({descripcion})")

                #archivo_audio = os.path.join(directorio, f"audio_{lang}_{tld}.mp3")
                # archivo_audio = os.path.join(directorio, f"audio_fr_ca.mp3")
                # Reproducir el archivo de audio
                # estos parametros son los que mejor suenan audio =fr_ca es com.mx,
                #reproducir_audio(archivo_audio, 1.5, .54, efecto="distort")

            except Exception as e:
                print(f"No se pudo guardar o reproducir el archivo para el TLD {tld}. Error: {e}")

def prueba_filtro(archivo_audio, text):
    # Configuración del idioma y parámetros estos son los que mejor suenan
    lang = 'fr'
    tld = 'ca'
    descripcion = 'French (Canada)'
    velocidad = 1.7
    tono = 0.6

    # Lista de filtros de audio para probar
    filtros = [
        ("ninguno", ""),
        ("distorsión", "distort"),
        ("saturación", "overdrive"),
        ("eco", "aecho=0.8:0.88:60:0.4"),
        ("granulado", "atempo=1.0, aeval='sin(0.1*440*2*PI*t)':a"),
        ("modulación", "modulate=0.7:1.5"),
    ]

    # Crear objeto gTTS
    #tts = gTTS(text=text, lang=lang, slow=False, tld=tld)

    # Nombre del archivo
    #archivo_audio = os.path.join(directorio, f"audio_{lang}_{tld}.mp3")

    # Guardar el archivo de audio
    #tts.save(archivo_audio)
    print(f"Archivo guardado: {archivo_audio} ({descripcion})")

    # Aplicar y reproducir cada filtro
    for nombre_filtro, efecto in filtros:
        print(f"Aplicando filtro: {nombre_filtro}")
        # reproducir_audio(archivo_audio, velocidad=velocidad, tono=tono, efecto=efecto)
        reproducir_audio(archivo_audio, velocidad=velocidad, tono=tono, efecto=efecto)

def crea_reproduce(texto):
    #archivo_audio = genera_muestra_acentos(texto) # Crear archivo con todos los acentos que tiene Gtts usando el español
    # archivo_audio = genera_muestra_acentos(texto,tld="com.mx")  # Crear archivo con todos los acentos que tiene Gtts usando el español
    archivo_audio = genera_muestra_acentos(texto,tld="ca")  # Crear archivo con todos los acentos que tiene Gtts usando el español
    # archivo_audio = os.path.join(directorio, f"audio_fr_ca.mp3")
    # prueba_filtro(archivo_audio, text)
    reproducir_audio(archivo_audio, 1.58,.54)

def main(texto=None):
    # Configuración del parser de argumentos
    texto_predeterminado = "Genera y reproduce archivos de audio usando gTTS con filtros aplicados, acentuando palabras por ejemplo mama y mamá."
    parser = argparse.ArgumentParser(description=texto_predeterminado)
    parser.add_argument('texto', type=str, nargs='?', default=None, help="Texto a convertir en audio")

    # Parsear los argumentos
    args = parser.parse_args()

    # Usar el texto proporcionado o el texto por defecto
    texto_a_usar = texto if texto else args.texto if args.texto else texto_predeterminado

    # Llamar a la función con el texto proporcionado o el texto por defecto
    crea_reproduce(texto_a_usar)


if __name__ == '__main__':
    main()
    print("Todos los archivos han sido generados y reproducidos.")

