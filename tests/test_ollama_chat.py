import pytest
import random
import string
import builtins
from toolla.chat import Chat
from toolla.exceptions import (
    MessageTooLongException,
    AbortedToolException,
    ImageNotSupportedException,
)
from .tools import add, multiply, concat

def test_openai_compatible_client_clear_messages():
    chat = Chat(
        model="llama3.1",
        base_url="http://localhost:11434/v1",
        tools=[add],
    )
    r = chat("Hello")
    chat.clear_messages()
    messages = chat.get_messages()
    assert len(messages) == 1
    assert messages[0]["role"] == "system"

def test_ollama_llama3_add_tool():
    chat = Chat(
        model="llama3.1",
        base_url="http://localhost:11434/v1",
        tools=[add],
    )
    r = chat("What is 341+18?")
    assert r == 359

def test_ollama_llama3_add_tool_with_user_defined_system_prompt():
    chat = Chat(
        model="llama3.1",
        base_url="http://localhost:11434/v1",
        system="Complete all prompts in the style of a professor.",
        tools=[add],
    )
    r = chat("What is 341+18?")
    assert r == 359

def test_llama_concat_tool():
    chat = Chat(
        model="llama3.1",
        base_url="http://localhost:11434/v1",
        tools=[concat]
    )
    r = chat("Concatenate the strings dream and tremor")
    assert r == "dreamtremor"

def test_llama_image_not_supported():
    with pytest.raises(ImageNotSupportedException) as exc_info:
        chat = Chat(
            model="llama3.1",
            base_url="http://localhost:11434/v1",
        )
        chat(prompt="What is this an image of? Answer with one word.", image="./cat.jpg")
    assert str(exc_info.value) == "Error: Image content not supported by API."

def test_llama_multiple_tools():
    chat = Chat(
        model="llama3.1",
        base_url="http://localhost:11434/v1",
        tools=[add, multiply],
    )
    r = chat("What is (4*4911)+18?")
    assert r == 19662

def test_llama_large_message_fail():
    with pytest.raises(MessageTooLongException) as exc_info:
        characters = string.ascii_letters + string.digits + string.punctuation
        prompt = ''.join(random.choice(characters) for _ in range(2000000))
        chat = Chat(
            model="llama3.1",
            base_url="http://localhost:11434/v1",
        )
        r = chat(prompt=prompt)
    assert str(exc_info.value) == "Error: Message is too long"

def test_llama_disable_auto_execution_answer_no():
    with pytest.raises(AbortedToolException) as exc_info:
        builtins.input = lambda _: 'n'
        chat = Chat(
            model="llama3.1",
            base_url="http://localhost:11434/v1",
            tools=[add],
        )
        chat("What is 4911+18?", disable_auto_execution=True)
    assert str(exc_info.value) == "Error: User aborted tool use."
