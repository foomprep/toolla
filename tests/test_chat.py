from toolla.chat import Chat
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
    # assert failure

