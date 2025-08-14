#!/usr/bin/env python3
from typing import Dict, Type

SpeechRecog_Dict: Dict[str, Type] = {}

def SpeechRecogType(keyword: str):
    def decorator(cls: Type) -> Type:
        SpeechRecog_Dict[keyword.lower()] = cls
        return cls
    return decorator

def SpeechRecog(**kwargs) -> Type:
    type = kwargs.get("type", "").lower()
    if type not in SpeechRecog_Dict:
        raise ValueError(f"Unknown speech recognition type: {type}")
    return SpeechRecog_Dict[type](**kwargs)

# Usage: SpeechRecog(type="wisper") -> wisper_VoiceRec