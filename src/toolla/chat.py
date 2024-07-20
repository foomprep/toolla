from typing import List, Dict, Union, Callable
from pathlib import Path
from anthropic import Anthropic
from anthropic.types.tool_use_block import ToolUseBlock
from anthropic.types.text_block import TextBlock
from toolla.utils import (
    build_tool_schema,
    get_image_mime_type,
    load_file_base64
)

# Setup streaming
class Chat:
    def __init__(
        self, 
        model: str = "claude-3-5-sonnet-20240620",
        system: Union[str, None] = None,
        tools: List[Callable] = [],
        max_steps = 10,
    ):
        # TODO possibly move client outside
        # TODO add tool choice to force tooling
        self.client = Anthropic()
        self.model = model
        self.system = system
        self.max_steps = max_steps
        self.messages = []

        # TODO these will change when expanding to other models
        self.max_tokens = 4096
        self.max_chars = 1_000_000

        # Build tool definitions from fns
        if tools:
            self.tools = []
            self.tool_fns = {}
            for f in tools:
                self.tool_fns[f.__name__] = f
                tool_dict = build_tool_schema(f)
                self.tools.append(tool_dict)
        else:
            self.tools = []

    def __call__(
        self, 
        prompt: str, 
        image: Union[str, None] = None, # base64 string
    ):
        message = {
            "role": "user",
            "content": [
                { "type": "text", "text": prompt }
            ]
        }
        if image:
            fpath = Path(image)
            mtype = get_image_mime_type(fpath)
            image_string = load_file_base64(fpath) 
            message["content"].append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mtype,
                        "data": image_string
                    }
                }
            )
        self.messages.append(message)

        print(self.messages)
        # TODO assert if tool choice set, then tools is not None
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=self.max_tokens,
            tools=self.tools or [],
            system=self.system or '',
            messages=self.messages,
        )
 
        text_response = None
        function_response = None
        for content in response.content:
            if isinstance(content, TextBlock):
                self.messages.append({
                    "role": "assistant",
                    "content": content.text,
                })
                text_response = content.text
            if isinstance(content, ToolUseBlock):
                # TODO make async spinner
                fn_inputs = content.input
                function_response = self.tool_fns[content.name](**fn_inputs)
                if len(self.messages) < 2 * self.max_steps:
                    if response.stop_reason == 'tool_use':
                        self(f"\nFunction {content.name} was called and returned a value of {function_response}")
                    elif response.stop_reason == 'end_turn':
                        return text_response, function_response
                else:
                    print("Reached maxiumum number of steps.")
                    return text_response, function_response
        # Just in case
        return text_response, function_response
    
    def append_to_log(self, s: str):
        if len(self.chat_log) > self.max_chars:
            excess = len(s) - self.max_chars
            self.chat_log = self.chat_log[excess:] + s
        else:
            self.chat_log += s
