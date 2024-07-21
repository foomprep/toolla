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

# TODO setup streaming
class Chat:
    def __init__(
        self, 
        model: str = "claude-3-5-sonnet-20240620",
        system: Union[str, None] = None,
        tools: List[Callable] = [],
        max_steps = 10,
        print_output=False,
    ):
        # TODO add tool choice to force tooling
        self.client = Anthropic()
        self.model = model
        self.system = system
        self.max_steps = max_steps
        self.messages = []
        self.print_output = print_output

        # TODO change when expanding to other models
        self.max_tokens = 4096
        self.max_chars = 1_000_000

        # Build tool definitions from fns
        if tools:
            # TODO check that docstrings
            # match functions and are valid 
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
        current_fn_response = None,
        disable_auto_execution = False,
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
    
        # A bit hacky, should calculate exact length given messages
        if len(str(self.messages)) > self.max_chars:
            while len(str(self.messages)) > self.max_chars:
                self.messages.pop(0)

        # TODO assert if tool choice set, then tools is not None
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=self.max_tokens,
            tools=self.tools or [],
            system=self.system or '',
            messages=self.messages,
        )
 
        for content in response.content:
            if isinstance(content, TextBlock):
                self.messages.append({
                    "role": "assistant",
                    "content": content.text,
                })
                if self.print_output:
                    print(content.text)
                if response.stop_reason == 'end_turn':
                    return current_fn_response
            elif isinstance(content, ToolUseBlock):
                fn_inputs = content.input
                # TODO add try catch block and return error
                if disable_auto_execution:
                    print(f"Function {content.name} is about to be called with inputs: {fn_inputs}")
                    user_input = input("Do you want to run this function? (y/n): ")
                    if user_input.lower() not in ['y', 'Y']:
                        print("Function call aborted by user.")
                        return None
                r = self.tool_fns[content.name](**fn_inputs)
                if len(self.messages) < 2 * self.max_steps:
                    if response.stop_reason == 'tool_use':
                        return self(
                            prompt=f"\nFunction {content.name} was called and returned a value of {r}",
                            current_fn_response=r,
                            disable_auto_execution=disable_auto_execution,
                        )
                else:
                    print("Reached maxiumum number of steps, returning current tool response.")
                    return None
        return None
