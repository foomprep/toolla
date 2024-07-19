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
    ):
        # TODO possibly move client outside
        # TODO add tool choice to force tooling
        self.client = Anthropic()
        self.model = model
        self.system = system
        self.chat_log = ""

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
        self.append_to_log(f"Human: {prompt}\n") 
        messages = [
            {
                "role": "user",
                "content": [
                    { "type": "text", "text": self.chat_log }
                ]
            }
        ]
        if image:
            fpath = Path(image)
            mtype = get_image_mime_type(fpath)
            image_string = load_file_base64(fpath) 
            messages[0]["content"].append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mtype,
                        "data": image_string
                    }
                }
            )
             
        # TODO assert if tool choice set, then tools is not None
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=self.max_tokens,
            tools=self.tools or [],
            system=self.system or '',
            messages=messages,
        )
    
        text_response = None
        function_response = None
        # We assume the response is ordered with TextBlock first
        for content in response.content:
            if isinstance(content, TextBlock):
                self.append_to_log(f"AI: {content.text}\n")
                text_response = content.text
            if isinstance(content, ToolUseBlock):
                # TODO make async spinner
                fn_inputs = content.input
                print("Calling function", content.name)
                result = self.tool_fns[content.name](**fn_inputs)
                print("Done.")
                function_response = result
        return text_response, function_response
    
    def append_to_log(self, s: str):
        if len(self.chat_log) > self.max_chars:
            excess = len(s) - self.max_chars
            self.chat_log = self.chat_log[excess:] + s
        else:
            self.chat_log += s
