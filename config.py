#!/usr/bin/env python
import yaml

MM_Args = {}
LLM_Full_Args = {}
LLM_Small_Args = {}
Display_Args = {}
Audio_Args = {}
SpeechRecog_Args = {}
Common_Args = {}
Prompts = {}
Character = {}

with open("config.yaml", "r", encoding="UTF-8") as f:
    config = yaml.safe_load(f)
    Common_Args = config.get("Common", {})
    Prompts = config.get("Prompts", {})
    Character = config.get("Character", {})
    MM_Args = config.get("MemoryManager", {})
    LLM_Full_Args = config.get("LLM_Full", {})
    LLM_Small_Args = config.get("LLM_Small", {})
    Display_Args = config.get("Display", {})
    Audio_Args = config.get("Audio", {})
    SpeechRecog_Args = config.get("SpeechRecognition", {})