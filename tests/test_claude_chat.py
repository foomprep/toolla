import pytest
import os
import builtins
from toolla.chat import Chat
from toolla.exceptions import (
    MessageTooLongException,
    AbortedToolException,
    ModelNotSupportedException,
)
from toolla.models import models
from .tools import add, multiply, concat

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

def test_claude_disable_auto_execution_answer_no():
    with pytest.raises(AbortedToolException) as exc_info:
        builtins.input = lambda _: 'n'
        chat = Chat(model="gpt-4o", tools=[add])
        chat("What is (4*4911)+18?", disable_auto_execution=True)
    assert str(exc_info.value) == "Error: User aborted tool use."

def test_get_supported_models():
    supported_models = Chat.get_supported_models()
    assert supported_models == models

def test_invalid_model_fails():
    try:
        chat = Chat(model="an_invalid_model_name")
    except ModelNotSupportedException as e:
        assert e.message == "Error: Model not supported by library."

def test_anthropic_client_clear_messages():
    chat = Chat()
    chat("hello")
    print(chat.get_messages())
    chat.clear_messages()
    print(chat.get_messages())
    assert chat.get_messages() == []