from typing import List, Dict, Union, Callable
from anthropic import Anthropic
from anthropic.types.tool_use_block import ToolUseBlock
from anthropic.types.text_block import TextBlock

class Chat:
    def __init__(
        self, 
        model: str = "claude-3-5-sonnet-20240620",
        system: Union[str, None] = None,
        tools: Union[List[Dict], None] = None,
        tool_fns: Union[Dict, None] = None,
    ):
    # TODO possibly move client outside
    # TODO add tool choice to force tooling
        self.client = Anthropic()
        self.model = model
        self.tools = tools
        self.system = system
        # TODO this is hacky, there should be a way to guarantee 
        # the functions will be in the global scope
        self.tool_fns = tool_fns

    def __call__(
        self, 
        prompt, 
        max_tokens=1024,
    ):
        # TODO assert if tool choice set, then tools is not None
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=max_tokens,
            tools=self.tools or [],
            system=self.system or '',
            messages=[
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        )
    
        # We assume the response is ordered with TextBlock first
        for content in response.content:
            if isinstance(content, TextBlock):
                print(content.text)
            if isinstance(content, ToolUseBlock):
                # TODO make async spinner
                function_inputs = content.input
                print("Calling function", content.name)
                result = self.tool_fns[content.name](**function_inputs)
                print("Done.")
                return result
