from toolla.utils import build_tool_schema

def test_build_tool_schema():
    def add(x: float, y: int, z: str):
        """
        An adder function that allows for all types.

        x: The first number to add.
        y: The second number to add.
        z: The third variable.
        """
        return x + y

    schema = build_tool_schema(add)
    expected = {
        "name": "add",
        "description": "An adder function that allows for all types.",
        "input_schema": {
            "type": "object",
            "properties": {
                "x": {
                    "type": "number",
                    "description": "The first number to add."
                },
                "y": {
                    "type": "number",
                    "description": "The second number to add."
                },
                "z": {
                    "type": "string",
                    "description": "The third variable."
                }
            },
            "required": ["x", "y", "z"]
        },
    }
    assert schema == expected
