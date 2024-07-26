import os
import json
from typing import Union, List, Callable
from pathlib import Path
from openai import OpenAI

from toolla.utils import (
    get_image_mime_type, 
    load_file_base64, 
    build_openai_tool_schema,
)
from toolla.exceptions import (
    MessageTooLongException, 
    AbortedToolException
)

class OpenAIClient:
    def __init__(
        self,
        model: str = "gpt-4o",
        system: Union[str, None] = None,
        tools: List[Callable] = [],
        max_steps: int = 10,
        print_output: bool = False,
        api_key: Union[str, None] = None,
    ):
        self.client = OpenAI(api_key=api_key or os.environ.get("OPENAI_API_KEY"))
        self.model = model
        self.max_steps = max_steps
        self.messages = []
        self.print_output = print_output

        # TODO change based on model choice
        self.max_tokens = 4096
        self.max_chars = 900_000

        if system:
            self.messages.append(
                {
                    "role": "system",
                    "content": system,
                }
            )

        if tools:
            # TODO check that docstrings
            # match functions and are valid 
            self.tools = []
            self.tool_fns = {}
            for f in tools:
                self.tool_fns[f.__name__] = f
                tool_dict = build_openai_tool_schema(f)
                self.tools.append(tool_dict)
        else:
            self.tools = []
    
    def __call__(
        self,
        prompt: str,
        image: Union[str, None] = None,
        current_fn_response = None,
        disable_auto_execution = False,
    ):
        message = {
            "role": "user",
            "content": [
                { "type": "text", "text": prompt }
            ]
        }
        self.messages.append(message)
        if image:
            fpath = Path(image)
            mtype = get_image_mime_type(fpath)
            image_string = load_file_base64(fpath) 
            message["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mtype};base64,{image_string}"
                    }
                }
            )
    
        while len(str(self.messages)) > self.max_chars:
            self.messages.pop(0)
            if not self.messages:
                raise MessageTooLongException

        # OpenAI doesn't allow for empty tool list
        # TODO change to self.tools or None
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=self.messages,
            tools=self.tools,
        ) if self.tools else self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=self.messages,
        )
 
        for choice in response.choices:
            if choice.finish_reason == 'stop':
                # TODO should be moved outside of for loop?
                self.messages.append({
                    "role": "assistant",
                    "content": choice.message.content,
                })
                if self.print_output:
                    print(f"{choice.message.content}\n")
                return current_fn_response
            elif choice.finish_reason == 'tool_calls':
                function = choice.message.tool_calls[0].function
                if disable_auto_execution:
                    print(f"Function {function.name} is about to be called with inputs: {function.arguments}")
                    user_input = input("Do you want to run this function? (y/n): ")
                    if user_input.lower() not in ['y', 'Y']:
                        print("Function call aborted by user.")
                        raise AbortedToolException
                r = self.tool_fns[function.name](**json.loads(function.arguments))
                if len(self.messages) < 2 * self.max_steps:
                    return self(
                        prompt=f"\nFunction {function.name} was called and returned a value of {r}",
                        current_fn_response=r,
                        disable_auto_execution=disable_auto_execution,
                    )
                else:
                    print("Reached maxiumum number of steps, returning current tool response.")
                    return current_fn_response