#!/usr/bin/env python3
from typing import Dict, Type

TextGenerator_Dict: Dict[str, Type] = {}

def TextGenType(keyword: str):
    def decorator(cls: Type) -> Type:
        TextGenerator_Dict[keyword.lower()] = cls
        return cls
    return decorator

def TextGen(**kwargs) -> Type:
    type = kwargs.get("type", "").lower()
    if type not in TextGenerator_Dict:
        raise ValueError(f"Unknown text generator type: {type}")
    return TextGenerator_Dict[type](**kwargs)

# Usage: TextGen(type="ollama") -> ollama_Gen