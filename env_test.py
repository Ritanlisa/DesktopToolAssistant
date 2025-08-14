#!/usr/bin/env python

# Test python version
import sys

if sys.version_info < (3, 12):
    print("Python 3.12 or higher is preferred.")

# Test All Requirements
requirements = [
    "openai",
    "ampligraph",
    "live2d",
    "ChatTTS",
    "whisper",
    "ffmpeg-python",
    "torch",
    "torchvision",
    "pyaudio",
    "jinja2",
    "tensorflow",
    "pygame",
    "pyAudioAnalysis",
    "speechbrain",
    "ollama",
    "eyed3",
    "pydub",
    "hmmlearn",
    "imblearn",
    "plotly",
]
with open("requirements.txt") as f:
    requirements = f.read().splitlines()
    for req in requirements:
        try:
            __import__(req)
        except ImportError:
            print(f"Missing package: {req}")

# Test PyTorch
try:
    import torch

    print(f"PyTorch Version: {torch.__version__}")
    if not torch.cuda.is_available():
        print("CUDA is not available!")
    else:
        print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
except ImportError:
    print("Missing torch")
