# toolla

`toola` is a high level stateful wrapper for Claude models through the `anthropic` python SDK.  It contains a `Chat` class that keeps a history of the chat and also enables automatic tool use by adding functions to the chat.

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

system = "Complete all prompts in the style of a pirate."
chat = Chat(system=system, print_output=True)
chat("I'm George")
chat("What's my name?")
```
By default, `chat` does not print the text response of the model.  Set `print_output` to change. The `Chat` class keeps a stateful history of the chat up to the context length.  You can access it at any time as object variable `messages`
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
The format of the docstring is required.  The first line MUST be a description of the function.  Any remaining lines that contain the char `:` will be considered arguments to the function along with their descriptions.  The `Chat` class automatically generates tool schema to be used in the API when you create a `Chat` instance.  Simply pass in the functions you want to include as tools
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
Anthropic API allow for images.  To include an image in a model query add a string path to the call
```
chat(prompt="What is this image of?", image="./cat.jpg")
```
Currently only supports `jpeg`, `png`, `gif` and `webp` as per Anthropic docs.  The image is loaded as a base64 string and added to the query.  It is also added to the chat history along with text.

## Multi-Step Tool Use
`toolla` will execute multi-step tool by default based on the `stop_reason` in the response.  Specify  tools and the `Chat` class will recursively call itself up to a maximum steps to accomplish the task specified in the prompt
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
print(result) # 19662
```

## Some tips
When using the package for more complicated tasks some tips might be helpful.  The `Chat` object continues the multi-step process by taking the answer returned by the tool at that step and adding its result as a `user` message.  So, for the above example when the model returns with a stop response of `tool_use` for `add` tool, it will run the function, get the result and then add the message
```
{
    "role": "user",
    "content": "Function add was called and returned with a value of 19644"
}
```
This will continue until the model returns a stop reason of `end_turn`.  To guide the model to the right decisions it is best to return values from your defined tool functions that are informative.  For example, if defining a tool function that adds a user to mongo database, the function should return a value in <i>text</i> that explains whether it successfully added user or not, also including some key information like `_id` for the mongo entry.  Also, if there is an error you can simply just return the error as a string! 

## Upcoming features
- Streaming
