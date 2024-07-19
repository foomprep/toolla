from toolla.utils import build_tool_schema

def test_build_tool_schema():
    def add(x: float, y: int):
        """
        x: The first number to add.
        y: The second number to add.
        """
        return x + y

    schema = build_tool_schema(add)
    expected = {
        "type": "object",
        "properties": {
            "x": {
                "type": "number",
                "description": ""
            },
            "y": {
                "type": "number",
                "description": "A float or integer."
            }
        },
        "required": ["x", "y"]
    }
    assert schema == expected
