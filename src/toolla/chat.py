from typing import List, Dict, Union, Callable
from toolla.models import (
    models,
)
from toolla.exceptions import (
    ModelNotSupportedException,
)
from toolla.anthropic_client import AnthropicClient
from toolla.openai_client import OpenAIClient
from toolla.openai_compatible_client import OpenAICompatibleClient
from toolla.ollama_guided_client import OllamaGuidedClient

class Chat:
    def __init__(
        self, 
        model: str = "claude-3-5-sonnet-20240620",
        system: Union[str, None] = None,
        tools: List[Callable] = [],
        max_steps = 10,
        print_output=False,
        api_key: Union[str, None] = None,
        base_url: Union[str, None] = None,
        #ollama_guided: bool = False,
    ):
        # if ollama_guided:
        #     self.client = OllamaGuidedClient(
        #         model=model,
        #         base_url=base_url,
        #         system=system,
        #         tools=tools,
        #         max_steps=max_steps,
        #         print_output=print_output,
        #     )
        if base_url:
            self.client = OpenAICompatibleClient(
                model=model,
                tools=tools,
                max_steps=max_steps,
                print_output=print_output,
                base_url=base_url,
                system=system,
                api_key=api_key,
            )
        elif model in models["openai_models"]:
            self.client = OpenAIClient(
                model=model,
                system=system,
                tools=tools,
                max_steps=max_steps,
                print_output=print_output,
                api_key=api_key,
            )
        elif model in models["claude_models"]:
            self.client = AnthropicClient(
                model=model,
                system=system,
                tools=tools,
                max_steps=max_steps,
                print_output=print_output,
                api_key=api_key,
            )
        else:
            raise ModelNotSupportedException

    def __call__(
        self,
        prompt: str,
        image: Union[str, None] = None, # base64 string
        current_fn_response = None,
        disable_auto_execution = False,
    ):
        return self.client(
            prompt=prompt,
            image=image,
            current_fn_response=current_fn_response,
            disable_auto_execution=disable_auto_execution,
        )

    @classmethod
    def get_supported_models(cls):
        return models

    def get_messages(self):
        return self.client.messages
    
    def clear_messages(self):
        self.client.messages = [
            message for message in self.client.messages if message["role"]  == "system"
        ]
