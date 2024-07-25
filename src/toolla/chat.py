import os
import json
from typing import List, Dict, Union, Callable
from pathlib import Path
from openai import OpenAI
from anthropic import Anthropic
from together import Together
from anthropic.types.tool_use_block import ToolUseBlock
from anthropic.types.text_block import TextBlock
from toolla.utils import (
    build_claude_tool_schema,
    build_openai_tool_schema,
    get_image_mime_type,
    load_file_base64,
    extract_first_json_block,
)
from toolla.models import (
    models,
    default_tool_prompt,
)
from toolla.exceptions import (
    MessageTooLongException,
    ModelNotSupportedException,
    AbortedToolException,
    ImageNotSupportedException,
)
from toolla.anthropic_client import AnthropicClient
from toolla.openai_client import OpenAIClient
from toolla.together_client import TogetherClient

class Chat:
    def __init__(
        self, 
        model: str = "claude-3-5-sonnet-20240620",
        system: Union[str, None] = None,
        tools: List[Callable] = [],
        max_steps = 10,
        print_output=False,
        api_key: Union[str, None] = None,
    ):
        if model in models["openai_models"]:
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
        elif model in models["together_models"]:
            self.client = TogetherClient(
                model=model,
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
