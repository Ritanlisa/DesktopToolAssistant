from typing import Iterable, Literal
import openai
from .general import TextGenType
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
    
    def generate(self, messages : Iterable[ChatCompletionMessageParam] = [], regex: str = "") -> str:
        if messages is None:
            messages = []

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        return response.choices[0].message.content