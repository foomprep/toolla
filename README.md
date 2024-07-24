# toolla

`toola` is a high level stateful wrapper for LLMs.  It contains a `Chat` class that keeps a history of the chat and also enables automatic tool use by defining python functions. It currently supports all GPT and Claude models with vision capabilities as well as models through [Together AI](https://www.together.ai/).  Tests have only been done for Llama models from Together but it should also work for others like Mistral.  The package aims to be as general as possible with respect to tool use.  Instead of including a suite of tools it allows the user to define their own tools using documented function definitions.  As a design choice, the package does not include streaming.  It assumes the end user will be using it in an interpreter/notebook environment.

## Installation
```
pip install toolla
```

## Quickstart
The library expects an API key in the environment.  You can also pass it as parameter `api_key` to the `Chat` constructor
```
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=..
export TOGETHER_API_KEY=..
```
or
```
chat = Chat(api_key='...')
```

You can use the chat normally without tools
```
from toolla.chat import Chat

system = "Complete all prompts in the style of a pirate."
chat = Chat(system=system, print_output=True)
chat("Hello")
```
By default, `chat` does not print the text response of the model.  Set `print_output=True` to view messages to `stdout`. The `Chat` class keeps a stateful history of the chat up to the context length.  You can get the chat history at any time with a getter
```
print(chat.get_messages())
```
`chat` only returns values when it uses tools, otherwise `None`.  When multiple tools are used, it will return the value of the <b>LAST</b> tool to be used. To use tools, define the function for a tool with documentation
```
def add(x: int, y: int) -> int:
    """
    A function that adds two numbers

    x: The first integer
    y: The second integer
    """
    return x + y
```
The docstring and its format is required.  The first line MUST be a description of the function.  Any remaining lines that contain the char `:` will be considered arguments to the function along with their descriptions.  The `Chat` class automatically generates tool schema to be used in the API when you create a `Chat` instance.  Pass in the functions you want to include as tools
```
tool_chat = Chat(tools=[add])
```
Then call `chat` to use the tool
```
summed = tool_chat("What is 4911+4131?")
print(summed) # 9042
```
⚠️ **Warning**
By default, the `chat` will <i>automatically</i> use tool functions as they are called by the model.  To disable automatic execution pass in a flag when instantiating the `Chat` object
```
summed = tool_chat("What is 4911+4131?", disable_auto_execution=True)
```

## Images
To include an image in a model query add a string path to the call
```
chat(prompt="What is this image of?", image="./cat.jpg")
```
Currently supports `jpeg`, `png`, `gif` and `webp`.  The image is added to the prompt as a base64 string but is excluded from the chat state so that it doesn't quickly grow larger than the model context window.

## Multi-Step Tool Use
`toolla` will execute multi-step tool by default based on the response of the model.  Specify tools and the `Chat` class will recursively call itself up to a maximum steps to accomplish the task specified in the prompt
```
def multiply(x: int, y: int) -> int:
    """
    A function for multiplying two integers.

    x: The first integer
    y: The second integer
    """
    return x * y

chat = Chat(tools=[add, multiply], max_steps=5) # Default is 10
result = chat("What is (4*4911)+18?")
print(chat.get_messages()) # chat state
print(result) # 19662
```
If the call reaches `max_steps`, execution will be stopped and the return value from the last tool used will be returned to the caller.

## Some tips
When using the package for more complicated tasks some tips might be helpful.  The `Chat` object continues the multi-step process by taking the answer returned by the tool at that step and adding its result as a `user` message.  So, for the above example when the model responds with tool for `add` tool, it will run the function, get the result and then add the message
```
{
    "role": "user",
    "content": "Function add was called and returned with a value of 19644"
}
```
This will continue until the stated task is completed (or `max_steps` is reached).  To guide the model to the right decisions it is best to return values from your defined tool functions that are informative.  For example, if defining a tool function that adds a user to a mongo database, the function should return a value in <i>text</i> that explains whether it successfully added user or not, also including some key information like `_id` or even entire user object for the mongo entry.  Also, if there is an error you can simply just return the error as a string! 
