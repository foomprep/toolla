from toolla.chat import Chat

def add(x: int, y: int) -> int:
    """
    A function for adding two integers.

    x: The first integer
    y: The second integer
    """
    return x + y

def test_tool_use():
    chat = Chat(
        tools=[add], 
    )
    r = chat("What is 2+3?")
    assert r == 5
