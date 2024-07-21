from toolla.chat import Chat
from tools import add, multiply, concat

def test_concat_tool():
    chat = Chat(tools=[concat])
    r = chat("Concatenate the strings dream and tremor")
    assert r == "dreamtremor"

def test_add_tool():
    chat = Chat(
        tools=[add], 
    )
    r = chat("What is 2+3?")
    assert r == 5

def test_chat_image_content():
    chat = Chat()
    chat(prompt="What is this an image of? Answer with one word.", image="./tests/cat.jpg")
    assert 'Cat' in chat.messages[-1]['content'] or 'cat' in chat.messages[-1]['content']

def test_multiple_tools():
    chat = Chat(tools=[add, multiply], max_steps=5)
    r = chat("What is (4*4911)+18?")
    assert r == 19662
