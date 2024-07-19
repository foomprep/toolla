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
    r = chat("Concatenate the strings dream and tremor")
    assert r == "dreamtremor"

def test_add_tool():
    chat = Chat(
        tools=[add], 
    )
    r = chat("What is 2+3?")
    assert r == 5
