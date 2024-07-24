import pytest
import os
import builtins
from toolla.chat import (
    Chat,
    MessageTooLongException,
    AbortedToolException,
    ModelNotSupportedException,
)
from toolla.models import models
from .tools import add, multiply, concat

def test_llama3_1_405b_instruct_turbo_add_tool():
    chat = Chat(model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo", tools=[add])
    r = chat("What is 341+18?")
    assert r == 359

def test_llama_concat_tool():
    chat = Chat(model="gpt-4o", tools=[concat])
    r = chat("Concatenate the strings dream and tremor")
    assert r == "dreamtremor"

def test_llama_image_content():
    chat = Chat(model="gpt-4o")
    chat(prompt="What is this an image of? Answer with one word.", image="./tests/cat.jpg")
    messages = chat.get_messages()
    assert 'Cat' in messages[-1]['content'] or 'cat' in messages[-1]['content']

def test_llama_multiple_tools():
    chat = Chat(model="gpt-4o", tools=[add, multiply])
    r = chat("What is (4*4911)+18?")
    assert r == 19662

def test_llama_large_message_fail():
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

def test_llama_disable_auto_execution_answer_no():
    with pytest.raises(AbortedToolException) as exc_info:
        builtins.input = lambda _: 'n'
        chat = Chat(model="gpt-4o", tools=[add])
        chat("What is (4*4911)+18?", disable_auto_execution=True)
    assert str(exc_info.value) == "Error: User aborted tool use."
