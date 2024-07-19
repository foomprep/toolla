from toolla.chat import Chat

def add(x, y) -> int:
    return x + y

add_tool = {
    "name": "add",
    "description": "Simple adding tool",
    "input_schema": {
        "type": "object",
        "properties": {
            "x": {
                "type": "number",
                "description": "A float or integer."
            },
            "y": {
                "type": "number",
                "description": "A float or integer."
            }
        },
        "required": ["x", "y"]
    }
}

def test_tool_use():
    chat = Chat(
        tools=[add_tool], 
        tool_fns={'add': add}
    )
    r = chat("What is 2+3?")
    assert r == 5
