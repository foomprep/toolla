import os
from typing import Union, List, Callable
from pathlib import Path
from together import Together
from toolla.exceptions import (
    ImageNotSupportedException,
    MessageTooLongException,
    AbortedToolException
)
from toolla.utils import (
    extract_first_json_block,
    build_claude_tool_schema,
)
from toolla.models import default_tool_prompt

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

