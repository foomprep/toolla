# toolla

`toola` is a stateful wrapper for the Anthropic API tool use.  It has a `Chat` class that will <i>automatically</i> execute functions that are passed to the chat as tools.  

## Installation
```
pip install toolla
```
In order to make calls to the Anthropic API you must have the `ANTHROPIC_API_KEY` environment variable set.
```
export ANTHROPIC_API_KEY=...
```

## Quickstart
You can use the chat normally without tools as
```
from toolla.chat import Chat

sp = "Complete all prompts in the style of a pirate."
chat = Chat(system=sp)
text_response, _ = chat("I'm George")
print(text_response)
text_response, _ = chat("What's my name?")
print(text_response)
```

Calling `chat` returns both the `TextBlock` response and if a tool is used, the value that is returned by the function corresponding to that tool. To use tools, define the function for a tool
```
def add(x: int, y: int) -> int:
    """
    A function that adds two numbers

    x: The first integer
    y: The second integer
    """
    return x + y
```
The format of the docstring is important.  The first line MUST be a description of the function.  Any remaining lines that contain the char `:` will be considered arguments to the function along with their descriptions.  The `Chat` class automatically generates tool schema to be used in the API when you create a `Chat` instance.  Simply pass in the functions you want to include as tools
```
tool_chat = Chat(tools=[add])
```
Then call `chat` to use the tool
```
text_response, function_response = tool_chat("What is 4911+4131?")
print(function_response)
```
The `result` variable will store whatever is returned by the tool.  Text responses will be printed to `stdout`.  You should see text printed similar to 
```
Calling function add
Done.
9042
```
