#!/usr/bin/env python3
from typing import Dict, Type

Displayer_Dict: Dict[str, Type] = {}

def DisplayerType(keyword: str):
    def decorator(cls: Type) -> Type:
        Displayer_Dict[keyword.lower()] = cls
        return cls
    return decorator

def Displayer(**kwargs) -> Type:
    type = kwargs.get("type", "").lower()
    if type not in Displayer_Dict:
        raise ValueError(f"Unknown displayer type: {type}")
    return Displayer_Dict[type](**kwargs)

# Usage: Displayer(type="live2D") -> live2D_displayer