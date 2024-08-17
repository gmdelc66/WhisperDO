# Whisper Full (& Offline) Install Process for Ubuntu

Purpose: These instructions cover the steps needed to install Whisper on Ubuntu, both for online and offline
installations.
Requirements:

    Full admin rights on your system.
    A computer with a CUDA-capable dedicated GPU with at least 4GB of VRAM (more VRAM is better). See: Available models and languages.
    For online installation: An Internet connection for the initial download and setup.
    For offline installation: Download the necessary files on another computer and then manually install them using the "OPTIONAL/OFFLINE" instructions below.

# Whisper Full (& Offline) Install Process for Ubuntu

## Purpose

These instructions cover the steps needed to install Whisper on Ubuntu, both for online and offline installations.

## Requirements

- **Full admin rights** on your system.
- A computer with a **CUDA-capable dedicated GPU** with at least 4GB of VRAM (more VRAM is better).
  See: [Available models and languages](https://github.com/openai/whisper#available-models-and-languages).
- **For online installation:** An Internet connection for the initial download and setup.
- **For offline installation:** Download the necessary files on another computer and then manually install them using
  the "OPTIONAL/OFFLINE" instructions below.

## Installation

### Step 1: Unlisted Pre-Requisites

Before you can run Whisper, you must install the following items. (For offline installation, download the files on
another machine and move them to your offline machine to install them.)

#### 1. NVIDIA CUDA Toolkit:

- Install the CUDA toolkit by following the [official instructions](https://developer.nvidia.com/cuda-downloads).
- Make sure to reboot your system after the installation.

#### 2. Python 3.9 or 3.10:

- Install Python using `apt`:

    ```bash
    sudo apt update
    sudo apt install python3.9 python3.9-venv python3.9-dev
    ```

- Verify the installation:

    ```bash
    python3.9 --version
    ```

#### 3. FFmpeg:

- Install FFmpeg:

    ```bash
    sudo apt install ffmpeg
    ```

#### 4. Git:

- Install Git:

    ```bash
    sudo apt install git
    ```

### Step 2A: Whisper Install (Online Install for Online Use)

- Open a terminal and type the following command:

    ```bash
    pip install git+https://github.com/openai/whisper.git
    ```

- Whisper is now ready to use online, and no further steps are required.

### Step 2B: Whisper Install (Online Install for Later Offline Use)

- Open a terminal and type the following commands:

    ```bash
    pip install git+https://github.com/openai/whisper.git
    pip install blobfile
    ```

- Continue to Step 3: Download Other Required Files.

### Step 2C: Whisper Install (Offline Install for Later Offline Use)

#### Option 1: Get the Most Up-to-Date Version of Whisper

1. Install Python and Git from Step 1 on another computer that can connect to the internet, and reboot to ensure both
   are working.
2. On the online machine, open a terminal in any empty folder and type the following commands:

    ```bash
    pip download git+https://github.com/openai/whisper.git
    pip download blobfile
    ```

3. Transfer the downloaded files to your offline machine.
4. On the offline machine, open a terminal in the folder where you placed the files, and run:

    ```bash
    pip install whisper*.whl
    pip install blobfile*.whl
    ```

#### Option 2: Download All the Necessary Files from Here

- Download the files from [OPENAI-Whisper-20230314 Offline Install Package](https://example.com).
- Transfer the files to your offline machine and open a terminal in the folder where you put the files, then run:

    ```bash
    pip install openai-whisper-20230314.zip
    pip install blobfile-2.0.2-py3-none-any.whl
    ```

- Continue to Step 3: Download Other Required Files.

### Step 3: Download Other Required Files (for Offline Use)

- Download Whisper's Language Model files and place them in `~/.cache/whisper`. If the links are dead, updated links can
  be found at lines 17-27 [here](https://example.com/init.py).
    - `Tiny.En`
    - `Tiny`
    - `Base.En`
    - `Base`
    - `Small.En`
    - `Small`
    - `Medium.En`
    - `Medium`
    - `Large-v1`
    - `Large-v2` (Announcing the large-v2 model)

- Download Whisper's vocabulary and encoder files:
    - Download `Vocab.bpe`
    - Download `Encoder.json`
    - Install the files to a folder of your choosing, e.g., `~/.cache/whisper`.
    - Update file links in your local copy of `openai_public.py` which will be installed in your Python folder, e.g.,
      `/usr/local/lib/python3.9/site-packages/tiktoken_ext/openai_public.py` to point to where you downloaded the files.
        - Remove the URL `https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/` and replace it with your
          local copy, e.g., `~/.cache/whisper/vocab.bpe` and `~/.cache/whisper/encoder.json`.

    ```python
    def gpt2():
        mergeable_ranks = data_gym_to_mergeable_bpe_ranks(
            vocab_bpe_file="~/.cache/whisper/vocab.bpe",
            encoder_json_file="~/.cache/whisper/encoder.json",
        )
    ```

## Alternative Offline Method

- See the pre-compiled .exe version of Whisper provided [here](https://example.com): Purfview / Whisper Standalone.

This guide should help you install Whisper on Ubuntu, whether you have an online connection or need to install it
offline.
