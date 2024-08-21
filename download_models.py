import hashlib
import io
import os
import urllib
import warnings
from typing import List, Optional, Union

import torch
from tqdm import tqdm

import speech_recognition as sr

# URLs de los modelos de Whisper
_MODELS = {
    "tiny.en": "https://openaipublic.azureedge.net/main/whisper/models/d3dd57d32accea0b295c96e26691aa14d8822fac7d9d27d5dc00b4ca2826dd03/tiny.en.pt",
    "base.en": "https://openaipublic.azureedge.net/main/whisper/models/25a8566e1d0c1e2231d1c762132cd20e0f96a85d16145c3a00adf5d1ac670ead/base.en.pt",
    "small.en": "https://openaipublic.azureedge.net/main/whisper/models/f953ad0fd29cacd07d5a9eda5624af0f6bcf2258be67c92b79389873d91e0872/small.en.pt",
    "medium.en": "https://openaipublic.azureedge.net/main/whisper/models/d7440d1dc186f76616474e0ff0b3b6b879abc9d1a4926b7adfa41db2d497ab4f/medium.en.pt",
    "large-v2": "https://openaipublic.azureedge.net/main/whisper/models/81f7c96c852ee8fc832187b0132e569d6c3065a3252ed18e56effd0b6a73e524/large-v2.pt",
}


# Descarga del modelo
def _download(url: str, root: str, in_memory: bool) -> Union[bytes, str]:
    os.makedirs(os.path.join(root, "models"), exist_ok=True)
    expected_sha256 = url.split("/")[-2]
    file_name = os.path.basename(url)
    download_target = os.path.join(root, "models", file_name)

    if os.path.exists(download_target) and os.path.isfile(download_target):
        with open(download_target, "rb") as f:
            model_bytes = f.read()
        if hashlib.sha256(model_bytes).hexdigest() == expected_sha256:
            return model_bytes if in_memory else download_target
        else:
            warnings.warn(f"{download_target} checksum does not match; re-downloading.")

    with urllib.request.urlopen(url) as source, open(download_target, "wb") as output:
        with tqdm(total=int(source.info().get("Content-Length")), ncols=80, unit="iB", unit_scale=True,
                  unit_divisor=1024) as loop:
            while True:
                buffer = source.read(8192)
                if not buffer:
                    break
                output.write(buffer)
                loop.update(len(buffer))

    model_bytes = open(download_target, "rb").read()
    if hashlib.sha256(model_bytes).hexdigest() != expected_sha256:
        raise RuntimeError("Model download failed checksum validation.")

    return model_bytes if in_memory else download_target


# Carga del modelo
def load_model(name: str, device: Optional[Union[str, torch.device]] = None, download_root: str = None,
               in_memory: bool = False):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if download_root is None:
        download_root = os.path.join(os.path.expanduser("~"), ".cache", "whisper")

    if name in _MODELS:
        checkpoint_file = _download(_MODELS[name], download_root, in_memory)
    else:
        raise RuntimeError(f"Model {name} not found; available models = {list(_MODELS.keys())}")

    with (io.BytesIO(checkpoint_file) if in_memory else open(checkpoint_file, "rb")) as fp:
        checkpoint = torch.load(fp, map_location=device)

    from whisper.model import Whisper, ModelDimensions
    dims = ModelDimensions(**checkpoint["dims"])
    model = Whisper(dims)
    model.load_state_dict(checkpoint["model_state_dict"])

    return model.to(device)


# Uso alternativo de speech_recognition si no hay GPU
def transcribe_with_speech_recognition(audio_file: str) -> str:
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return "Speech Recognition could not understand the audio"
    except sr.RequestError:
        return "Could not request results from Speech Recognition service"


# Uso del modelo
def transcribe_audio(audio_file: str, model_name: str = "base.en"):
    if torch.cuda.is_available():
        model = load_model(model_name)
        # Aquí puedes llamar a la función `transcribe` del modelo cargado
        result = transcribe(model, audio_file)
        return result
    else:
        return transcribe_with_speech_recognition(audio_file)


# Ejemplo de uso
audio_file_path = "/home/kitty/Downloads/lucia.mp3"
transcription = transcribe_audio(audio_file_path)
print(transcription)
