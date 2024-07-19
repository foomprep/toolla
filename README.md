# toolla

`toola` is a simple wrapper for the Anthropic API tool use.  It has a `Chat` class that will <i>automatically</i> execute functions that are passed to the chat as tools.

## Installation
```
pip install toolla
```
In order to make calls to the Anthropic API you must have the `ANTHROPIC_API_KEY` environment variable set.
```
export ANTHROPIC_API_KEY=...
```

## Quickstart
Begin by defining the functions you'd like to use as tools
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
from toolla.chat import Chat

chat = Chat(tools=[add])
```
Then call `chat` to use the tool
```
result = chat("What is 4911+4131?")
print(result)
```
The `result` variable will store whatever is returned by the tool.  Text responses will be printed to `stdout`.  You should see text printed similar to 
```
To answer your question about what 4911 + 4131 is, I can use the "add" function that's available to me. Let me calculate that for you.
Calling function add
Done.
9042
```
