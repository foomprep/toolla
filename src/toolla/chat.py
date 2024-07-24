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

# TODO add option to include images in chat state

class AnthropicClient:
    def __init__(
        self,
        model: str,
        system: Union[str, None] = None,
        tools: List[Dict] = [],
        max_steps = 10,
        print_output=False,
        api_key: Union[str, None] = None,
    ):
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
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
                tool_dict = build_claude_tool_schema(f)
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
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mtype,
                        "data": image_string
                    }
                }
            )
    
        # A bit hacky, should calculate exact length given messages
        while len(str(self.messages)) > self.max_chars:
            self.messages.pop(0)
            if not self.messages:
                raise MessageTooLongException

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
                    print(f"{content.text}\n")
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
                        raise AbortedToolException
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
                
class TogetherClient:
    def __init__(
        self,
        model: str,
        #system: Union[str, None] = None,   Disable for now, use default prompt
        tools: List[Callable] = [],
        max_steps = 10,
        print_output=False,
        api_key: Union[str, None] = None,
    ):
        self.client = Together(api_key=api_key or os.environ.get("TOGETHER_API_KEY"))
        self.model = model
        # self.system = system
        self.max_steps = max_steps
        self.messages = []
        self.print_output = print_output

        # TODO change based on model choice
        # self.max_tokens = 4096
        self.max_chars = 900_000

        if tools:
            # TODO check that docstrings
            # match functions and are valid 
            self.tools = []
            self.tool_fns = {}
            for f in tools:
                self.tool_fns[f.__name__] = f
                tool_dict = build_claude_tool_schema(f)
                self.tools.append(tool_dict)
        else:
            self.tools = []

        self.messages.append(
            {
                "role": "system",
                "content": default_tool_prompt.format(tool_list=str(self.tools)),
            }
        )
        
    def __call__(
        self,
        prompt: str,
        image: Union[str, None] = None,
        current_fn_response = None,
        disable_auto_execution = False,
    ):
        message = {
            "role": "user",
            "content": prompt,
        }
        self.messages.append(message)
        # TODO Together does not currently support images
        # if image:
        #     fpath = Path(image)
        #     mtype = get_image_mime_type(fpath)
        #     image_string = load_file_base64(fpath) 
        #     message["content"] += f"\nImage Data:\ndata:{mtype};base64,{image_string}"
        if image:
            raise ImageNotSupportedException
    
        while len(str(self.messages)) > self.max_chars:
            self.messages.pop(0)
            if not self.messages:
                raise MessageTooLongException

        print("Messages: ", self.messages)
        response = self.client.chat.completions.create(
            model=self.model,
            # max_tokens=self.max_tokens,
            messages=self.messages,
        )
        self.messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content,
        })
        if self.print_output:
            print(f"{response.choices[0].message.content}\n")
        parsed_response = extract_first_json_block(response.choices[0].message.content)
        if parsed_response:
            if disable_auto_execution:
                print(f"Function {parsed_response['tool']} is about to be called with inputs: {parsed_response['inputs']}")
                user_input = input("Do you want to run this function? (y/n): ")
                if user_input.lower() not in ['y', 'Y']:
                    print("Function call aborted by user.")
                    raise AbortedToolException
            r = self.tool_fns[parsed_response['tool']](**parsed_response['inputs'])
            if len(self.messages) < 2 * self.max_steps:
                return self(
                    prompt=f"\nFunction {parsed_response['tool']} was called and returned a value of {r}",
                    current_fn_response=r,
                    disable_auto_execution=disable_auto_execution,
                )
            else:
                print("Reached maxiumum number of steps, returning current tool response.")
                return current_fn_response
        else:
            return current_fn_response

# TODO setup streaming
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
