#!/usr/bin/env python3
import re
import requests
from typing import Any, Literal, Mapping, Optional, Sequence, Union
from ollama import Client, Message, ChatResponse
from pydantic.json_schema import JsonSchemaValue
from .general import TextGenType

@TextGenType("ollama")
class ollama_Gen:
    def __init__(self, model: str, api_key: str, base_url: str = "http://localhost:11434", type: Literal["ollama", "Ollama"] = "Ollama", support_cot: bool = False):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.support_cot = support_cot

        # Create session with API key in headers
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = Client(host=base_url, headers=headers)

    @staticmethod
    def support_regex_limitation():
        return True
    
    @staticmethod
    def __regex_formatter(regex_expression: str):
        # 1. check regex expression if it's valid
        try:
            re.compile(regex_expression)
        except re.error:
            raise ValueError(f"Invalid regex: {regex_expression}")
        
        # 2. make anchors
        if not regex_expression.startswith("^"):
            regex_expression = "^" + regex_expression
        if not regex_expression.endswith("$"):
            regex_expression = regex_expression + "$"
        
        # 3. replace expressions which will touch bugs
        # i. (?:) -> () 
        regex_expression = regex_expression.replace(r"(?:" , r"(")
        # ii. \d -> [0-9]
        regex_expression = regex_expression.replace(r"\d", r"[0-9]")
        regex_expression = regex_expression.replace(r"\D", r"[^0-9]")
        # iii. \w -> [a-zA-Z0-9_]
        regex_expression = regex_expression.replace(r"\w", r"[a-zA-Z0-9_]")
        regex_expression = regex_expression.replace(r"\W", r"[^a-zA-Z0-9_]")
        # iv. \s -> [ \t\n\r\f\v]
        regex_expression = regex_expression.replace(r"\s", r"[ \t\n\r\f\v]")
        regex_expression = regex_expression.replace(r"\S", r"[^ \t\n\r\f\v]")

        # final check: this should be valid
        try:
            re.compile(regex_expression)
        except re.error:
            raise AssertionError(f"Invalid regex occurred after formatted regex: {regex_expression}")
        return regex_expression

    def generate(self, messages: Optional[Sequence[Union[Mapping[str, Any], Message]]] = None, regex: str = "") -> str:
        if regex == "":
            response: ChatResponse = self.client.chat(
                model=self.model,
                messages=messages
            )
            return response['message']['content']
        else:
            # Generate without regex constraint first
            response: ChatResponse = self.client.chat(
                model=self.model,
                messages=messages,
                format=JsonSchemaValue({
                    "type": "string",
                    "pattern": ollama_Gen.__regex_formatter(regex)
                })
            )
            return response['message']['content'][1:-1]