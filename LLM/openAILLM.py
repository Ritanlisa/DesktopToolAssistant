import re
from typing import Iterable, Literal
import openai
from .general import TextGenType
from log import log
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam

@TextGenType("openAI")
class openAI_Gen:
    def __init__(self, model: str, api_key: str, base_url: str = "https://api.openai.com/v1", type: Literal["openAI", "OpenAI"] = "OpenAI", support_cot: bool = False):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.support_cot = support_cot

    @staticmethod
    def support_regex_limitation():
        return False
        
    def support_chain_of_thought(self):
        return self.support_cot
    
    def generate(self, messages : Iterable[ChatCompletionMessageParam] = [], regex: str = "", autoCOT: bool = True) -> str:
        if messages is None:
            messages = []

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        result: str = response.choices[0].message.content # type: ignore
        
        if autoCOT:
            match = re.search(r"^<think>\s*(.*)\s*</think>\s*(.*)\s*$", result)
            if match:
                # If we found a match, we can use it
                log("INFO", "OpenAI LLM", f"LLM Thought:{match.group(1)}")
                result = match.group(2)

        return result