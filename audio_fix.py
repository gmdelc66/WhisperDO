###################################################################################
##
# Author:      gatito
#
# Created:     1/sep/2024
# Copyright:   (c) gatito 2024 en postPandemia, antes de crisis Mexico
# Licence:     Licence MIT
###################################################################################

#     Este pipeline tomará un archivo de audio, aplicará las técnicas de
#     preprocesamiento, y devolverá el archivo procesado listo para ser
#     transcrito con Whisper.
#################################################################################3
# **************** NO AYUDAN EN NADA ARCHIVOS PARA WHISPER MODEL SMALL ***********
##################################################################################
from scipy.io import wavfile
import numpy as np
from pydub import AudioSegment

def remove_noise(audio_file):
    rate, data = wavfile.read(audio_file)
    # Aplicar Transformada de Fourier
    transformed_data = np.fft.fft(data)
    # Eliminar ruido (frecuencias bajas y altas)
    transformed_data[:100] = 0
    transformed_data[-100:] = 0
    # Reconstruir el audio
    clean_data = np.fft.ifft(transformed_data)
    wavfile.write(audio_file, rate, np.real(clean_data).astype(np.int16))
    return audio_file

def normalize_volume(audio_file):
    audio = AudioSegment.from_wav(audio_file)
    normalized_audio = audio.apply_gain(-audio.max_dBFS)  # Normalizar a 0 dBFS
    normalized_file = audio_file
    normalized_audio.export(normalized_file, format="wav")
    return normalized_file

def enhance_clarity(audio_file):
    audio = AudioSegment.from_wav(audio_file)
    # Aplicar un filtro de agudos para mejorar la claridad
    enhanced_audio = audio.high_pass_filter(300).low_pass_filter(3000)
    enhanced_file = audio_file
    enhanced_audio.export(enhanced_file, format="wav")
    return enhanced_file

def preprocess_audio(audio_file):
    #cleaned_file = remove_noise(audio_file)
    #normalized_file = normalize_volume(cleaned_file)
    #enhanced_file = enhance_clarity(normalized_file)
    enhanced_file = enhance_clarity(audio_file)
    return enhanced_file

# Uso del pipeline
# preprocessed_audio = preprocess_audio("input_audio.wav")
