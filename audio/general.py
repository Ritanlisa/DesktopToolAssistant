#!/usr/bin/env python3
from typing import Dict, Type

AudioGenerator_Dict: Dict[str, Type] = {}

def AudioGenType(keyword: str):
    def decorator(cls: Type) -> Type:
        AudioGenerator_Dict[keyword.lower()] = cls
        return cls
    return decorator

def AudioGen(**kwargs) -> Type:
    type = kwargs.get("type", "").lower()
    if type not in AudioGenerator_Dict:
        raise ValueError(f"Unknown audio generator type: {type}")
    return AudioGenerator_Dict[type](**kwargs)

# Usage: AudioGen(type="ChatTTS") -> ChatTTS_VoiceGen