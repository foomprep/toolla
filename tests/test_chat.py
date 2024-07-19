from toolla.chat import Chat

def add(x: int, y: int) -> int:
    """
    A function for adding two integers.

    x: The first integer
    y: The second integer
    """
    return x + y

def concat(first: str, second: str) -> str:
    """
    A leetle function to concatentate strings

    first: The first string
    second: The second string

    returns concatenated string
    """
    return first + second

def test_concat_tool():
    chat = Chat(tools=[concat])
    t, fr = chat("Concatenate the strings dream and tremor")
    assert fr == "dreamtremor"

def test_add_tool():
    chat = Chat(
        tools=[add], 
    )
    t, fr = chat("What is 2+3?")
    assert fr == 5

def test_chat_image_content():
    chat = Chat()
    t, fr = chat(prompt="What is this an image of? Answer with one word.", image="./tests/cat.jpg")
    assert "Cat" in t or "cat" in t, f"Expected 'Cat' in response, but got: {t}"
