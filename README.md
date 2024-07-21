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
You can use the chat normally without tools
```
from toolla.chat import Chat

sp = "Complete all prompts in the style of a pirate."
chat = Chat(system=sp, print_output=True)
chat("I'm George")
chat("What's my name?")
```
By default, `chat` does not print the text response of the model.  Set `print_output` to change. The `Chat` class keeps a stateful history of the chat up to the context length.
```
print(chat.messages)
```
`chat` only returns values when it uses tools.  The returned value is the return value of the LAST tool to be used. To use tools, define the function for a tool
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
summed = tool_chat("What is 4911+4131?")
print(summed)
```

## Images
Anthropic API allow for images.  To include an image in a model query add a string path to the call
```
chat(prompt="What is this image of?", image="./cat.jpg")
```
Currently only supports `jpeg`, `png`, `gif` and `webp` as per Anthropic docs.  The image is loaded as a base64 string and added to the query.  It is also added to the chat history along with text.

## Multi-step Multiple Tool Use
`toolla` will execute multi-step tool by default based on the stop reason in the response from Anthropic.  Using the `add` function above a with an additional `multiply` function, simply specify multiple tools and the `Chat` class will move step by step to get the result
```
def multiply(x: int, y: int) -> int:
    """
    A function for multiplying two integers.

    x: The first integer
    y: The second integer
    """
    return x * y

chat = Chat(tools=[add, multiply])
t, fr = chat("What is (4*4911)+18?")
print(f) # 19662
```
