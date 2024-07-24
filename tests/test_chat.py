import os
import builtins
from toolla.chat import (
    Chat,
    MessageTooLongException,
    AbortedToolException,
    ModelNotSupportedException,
)
from .tools import add, multiply, concat

def test_openai_add_tool():
    chat = Chat(model="gpt-4o", tools=[add])
    r = chat("What is 2+3?")
    assert r == 5

def test_openai_concat_tool():
    chat = Chat(model="gpt-4o", tools=[concat])
    r = chat("Concatenate the strings dream and tremor")
    assert r == "dreamtremor"

def test_openai_image_content():
    chat = Chat(model="gpt-4o")
    chat(prompt="What is this an image of? Answer with one word.", image="./tests/cat.jpg")
    messages = chat.get_messages()
    assert 'Cat' in messages[-1]['content'] or 'cat' in messages[-1]['content']

def test_openai_multiple_tools():
    chat = Chat(model="gpt-4o", tools=[add, multiply])
    r = chat("What is (4*4911)+18?")
    assert r == 19662

def test_openai_large_message_fail():
    try:
        with open('image.jpeg', 'wb') as f:
            f.write(b'\0' * 2000000)
        chat = Chat(model='gpt-4o')
        r = chat(prompt="What is this?", image='./image.jpeg')
    except MessageTooLongException as e:
        assert str(e) == "Error: Message is too long"
    finally:
        if os.path.exists('image.jpeg'):
            os.remove('image.jpeg')

def test_openai_disable_auto_execution_answer_no():
    builtins.input = lambda _: 'n'
    chat = Chat(model="gpt-4o", tools=[add])
    try:
        r = chat("What is (4*4911)+18?", disable_auto_execution=True)
    except AbortedToolException as e:
        assert e.message == "Error: User aborted tool use."

def test_claude_concat_tool():
    chat = Chat(tools=[concat])
    r = chat("Concatenate the strings dream and tremor")
    assert r == "dreamtremor"

def test_claude_add_tool():
    chat = Chat(tools=[add])
    r = chat("What is 2+3?")
    assert r == 5

def test_claude_chat_image_content():
    chat = Chat()
    chat(prompt="What is this an image of? Answer with one word.", image="./tests/cat.jpg")
    messages = chat.get_messages()
    assert 'Cat' in messages[-1]['content'] or 'cat' in messages[-1]['content']

def test_claude_multiple_tools():
    chat = Chat(tools=[add, multiply], max_steps=5)
    r = chat("What is (4*4911)+18?")
    assert r == 19662

def test_claude_large_message_fail():
    try:
        with open('image.jpeg', 'wb') as f:
            f.write(b'\0' * 2000000)
        chat = Chat()
        r = chat(prompt="What is this?", image='./image.jpeg')
    except MessageTooLongException as e:
        assert str(e) == "Error: Message is too long"
    finally:
        if os.path.exists('image.jpeg'):
            os.remove('image.jpeg')

def test_invalid_model_fails():
    try:
        chat = Chat(model="an_invalid_model_name")
    except ModelNotSupportedException as e:
        assert e.message == "Error: Model not supported by library."

def test_get_supported_models():
    supported_models = Chat.get_supported_models()

