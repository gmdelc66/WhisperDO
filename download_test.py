import os
import hashlib
import io
import urllib
import warnings
from typing import List, Optional, Union

import torch
from tqdm import tqdm
import whisper
import pytest
from whisper.tokenizer import get_tokenizer

import speech_recognition as sr

# URLs de los modelos de Whisper
_MODELS = {
"tiny.en": "https://openaipublic.azureedge.net/main/whisper/models/d3dd57d32accea0b295c96e26691aa14d8822fac7d9d27d5dc00b4ca2826dd03/tiny.en.pt",
"tiny": "https://openaipublic.azureedge.net/main/whisper/models/65147644a518d12f04e32d6f3b26facc3f8dd46e5390956a9424a650c0ce22b9/tiny.pt",
"base.en": "https://openaipublic.azureedge.net/main/whisper/models/25a8566e1d0c1e2231d1c762132cd20e0f96a85d16145c3a00adf5d1ac670ead/base.en.pt",
"base": "https://openaipublic.azureedge.net/main/whisper/models/ed3a0b6b1c0edf879ad9b11b1af5a0e6ab5db9205f891f668f8b0e6c6326e34e/base.pt",
"small.en": "https://openaipublic.azureedge.net/main/whisper/models/f953ad0fd29cacd07d5a9eda5624af0f6bcf2258be67c92b79389873d91e0872/small.en.pt",
"small": "https://openaipublic.azureedge.net/main/whisper/models/9ecf779972d90ba49c06d968637d720dd632c55bbf19d441fb42bf17a411e794/small.pt",
"medium.en": "https://openaipublic.azureedge.net/main/whisper/models/d7440d1dc186f76616474e0ff0b3b6b879abc9d1a4926b7adfa41db2d497ab4f/medium.en.pt",
"medium": "https://openaipublic.azureedge.net/main/whisper/models/345ae4da62f9b3d59415adc60127b97c714f32e89e936602e85993674d08dcb1/medium.pt",
"large-v1": "https://openaipublic.azureedge.net/main/whisper/models/e4b87e7e0bf463eb8e6956e646f1e277e901512310def2c24bf0e11bd3c28e9a/large-v1.pt",
"large-v2": "https://openaipublic.azureedge.net/main/whisper/models/81f7c96c852ee8fc832187b0132e569d6c3065a3252ed18e56effd0b6a73e524/large-v2.pt",
"large-v3": "https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt",
"large": "https://openaipublic.azureedge.net/main/whisper/models/e5b1a55b89c1367dacf97e3e19bfd829a01529dbfdeefa8caeb59b3f1b81dadb/large-v3.pt",
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

def transcribe(model, audio_file):
    result = model.transcribe(audio_file, temperature=0.0, word_timestamps=True)
    return result["text"]



# Prueba del modelo
@pytest.mark.parametrize("model_name", whisper.available_models())
def test_transcribe(model_name: str):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = load_model(model_name).to(device)
    audio_path = os.path.join(os.path.dirname(__file__), "jfk.flac")

    language = "en" if model_name.endswith(".en") else None
    result = model.transcribe(
        audio_path, language=language, temperature=0.0, word_timestamps=True
    )
    assert result["language"] == "en"
    assert result["text"] == "".join([s["text"] for s in result["segments"]])

    transcription = result["text"].lower()
    assert "my fellow americans" in transcription
    assert "your country" in transcription
    assert "do for you" in transcription

    tokenizer = get_tokenizer(model.is_multilingual, num_languages=model.num_languages)
    all_tokens = [t for s in result["segments"] for t in s["tokens"]]
    assert tokenizer.decode(all_tokens) == result["text"]
    assert tokenizer.decode_with_timestamps(all_tokens).startswith("<|0.00|>")

    timing_checked = False
    for segment in result["segments"]:
        for timing in segment["words"]:
            assert timing["start"] < timing["end"]
            if timing["word"].strip(" ,") == "Americans":
                assert timing["start"] <= 1.8
                assert timing["end"] >= 1.8
                timing_checked = True

    assert timing_checked

def transcribe_audio(audio_file: str, model_name: str = "base.en"):
    print(f"Starting transcription for {audio_file} using {model_name}")
    if torch.cuda.is_available():
        print("CUDA is available, using Whisper model.")
        model = load_model(model_name)
        result = transcribe(model, audio_file)
        print("Transcription complete:", result)
        return result
    else:
        print("CUDA not available, using speech recognition.")
        return transcribe_with_speech_recognition(audio_file)

if __name__ == '__main__':
    audio_file = "/home/kitty/Downloads/lucia.mp3"
    audio_file = "/home/kitty/Downloads/Project Name.mp4"
    model = "base"
    texto = transcribe_audio(audio_file, model)
    print(texto)