from typing import Union, List, Callable, get_type_hints
from openai import OpenAI
from toolla.exceptions import (
    ImageNotSupportedException,
    AbortedToolException,
    MessageTooLongException,
)
from toolla.utils import (
    build_openai_tool_schema,
    extract_json_from_text,
)
from toolla.models import default_tool_prompt

class OpenAICompatibleClient:
    def __init__(
        self,
        model: str,
        *,
        tools: List[Callable] = [],
        max_steps = 10,
        print_output=False,
        base_url: Union[str, None] = None,
        system: Union[str, None] = None,
        api_key: Union[str, None] = None,
    ):
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model = model
        self.max_steps = max_steps
        self.messages = []
        self.print_output = print_output
        self.max_chars = 900_000 # Totally random, figure something else out

        if tools:
            self.tools = []
            self.tool_fns = {}
            for f in tools:
                self.tool_fns[f.__name__] = f
                tool_dict = build_openai_tool_schema(f)
                self.tools.append(tool_dict)
        else:
            self.tools = []

        if system:
            system_prompt = system + default_tool_prompt.format(tool_list=str(self.tools))
        else:
            system_prompt = default_tool_prompt.format(tool_list=str(self.tools))
        self.messages.append(
            {
                "role": "system",
                "content": system_prompt,
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
        if image:
            raise ImageNotSupportedException
    
        while len(str(self.messages)) > self.max_chars:
            self.messages.pop(0)
            if not self.messages:
                raise MessageTooLongException

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )
        self.messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content,
        })
        if self.print_output:
            print(f"{response.choices[0].message.content}\n")
        if self.tools:
            parsed_response = extract_json_from_text(response.choices[0].message.content)
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
