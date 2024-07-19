from toolla.utils import build_tool_schema
from enum import Enum

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

def test_build_schema_with_enum():
    class Answer(Enum):
        YES = 1
        NO = 2

    def question(q: str, a: Answer) -> str:
        """
        Answer to a question

        q: The question
        a: The answer
        """
        pass
    
    schema = build_tool_schema(question)
    expected = {
        "name": "question",
        "description": "Answer to a question",
        "input_schema": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "The question"
                },
                "a": {
                    "type": "string",
                    "enum": ["YES", "NO"],
                    "description": "The answer"
                }
            },
            "required": ["q", "a"]
        },
    }
    print(schema)
    print(expected)
    assert schema == expected
