from typing import Union, List, Callable, get_type_hints
import requests
import json
from toolla.exceptions import (
    ImageNotSupportedException,
    AbortedToolException,
    MessageTooLongException,
)
from toolla.utils import (
    build_openai_tool_schema,
)

default_guided_gen_tool_prompt = """
You are a helpful assistant that can guide the user through a series of steps to solve a problem.  You have access to a list of Available Tools and will return current tool to use given the Return Tool Schema.  If no tool is needed return an empty JSON.  ONLY return tools that are within available tools.

Available Tools:
{tool_list}

Return Tool Schema:
{{ 
    'tool': '<name>', 
    'inputs': {{ 
        '<key>': '<value>'
    }} 
}}
"""

class OllamaGuidedClient:
    base_url: str

    def __init__(
        self,
        model: str,
        base_url: str,
        *,
        tools: List[Callable] = [],
        max_steps = 10,
        print_output=False,
        system: Union[str, None] = None,
    ):
        self.base_url = base_url
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

        self.messages.append(
            {
                "role": "system",
                "content": system or 
                    default_guided_gen_tool_prompt.format(tool_list=str(self.tools)),
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

        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": False,
        }
        response = requests.post(
            self.base_url + '/api/chat',
            json=payload,
        )
        # TODO catch error for bad response
        response_body = response.json()
        print(response_body)
        response_text = response_body['message']['content']
        self.messages.append({
            "role": "assistant",
            "content": response_text,
        })

        # Parse suggested tool using structured generation with same model
        # using ollama completion
        prompt = f"""Parse and return the JSON in the following text
        Text:
        {response_text} 
        """
        json_parser_payload = {
            "model": self.model,
            "prompt": prompt,
            "format": "json",
            "stream": False,
        }
        response = requests.post(
            self.base_url + '/api/generate',
            json=json_parser_payload,
        )
        suggested_tool = json.loads(response.json()['response'])
        print("Suggested tool: ", suggested_tool)

        if self.print_output:
            print(f"{response_text}\n")
        if self.tools:
            if parsed_response and parsed_response['tool']:
                if disable_auto_execution:
                    print(f"Function {parsed_response['tool']} is about to be called with inputs: {parsed_response['inputs']}")
                    user_input = input("Do you want to run this function? (y/n): ")
                    if user_input.lower() not in ['y', 'Y']:
                        print("Function call aborted by user.")
                        raise AbortedToolException
                hints = get_type_hints(self.tool_fns[parsed_response['tool']])
                for input in parsed_response['inputs']:
                    if isinstance(hints[input], int):
                        if isinstance(parsed_response['inputs'][input], str):
                            parsed_response['inputs'][input] = int(parsed_response['inputs'][input])
                        if isinstance(hints[input], float):
                            if isinstance(parsed_response['inputs'][input], str):
                                parsed_response['inputs'][input] = float(parsed_response['inputs'][input])

                print("Calling function with inputs: ", parsed_response['inputs'])
                print("Argument type hints are: ", get_type_hints(self.tool_fns[parsed_response['tool']]))
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
