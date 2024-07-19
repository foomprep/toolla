from toolla.utils import (
    build_tool_schema,
    load_file_base64,
    get_image_mime_type
)
from enum import Enum
import base64
from pathlib import Path

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

def test_load_file_base64():
    # Create a temporary file with some content
    test_file = Path("test_file.txt")
    test_content = b"Hello, World!"
    test_file.write_bytes(test_content)

    try:
        # Test the function
        result = load_file_base64(test_file)
        expected = base64.b64encode(test_content).decode('utf-8')
        assert result == expected
    finally:
        # Clean up the temporary file
        test_file.unlink()

def test_get_jpeg_mime():
    fpath = Path('arrakis.jpg')
    t = get_image_mime_type(fpath)
    assert t == "image/jpeg"

def test_get_jpeg_alt_mime():
    fpath = Path('dune.jpeg')
    t = get_image_mime_type(fpath)
    assert t == "image/jpeg"

def test_get_gif_mime():
    fpath = Path('sandworm.gif')
    t = get_image_mime_type(fpath)
    assert t == "image/gif"

def test_get_png_mime():
    fpath = Path('fremen.png')
    t = get_image_mime_type(fpath)
    assert t == "image/png"

def test_get_webp_mime():
    fpath = Path('spice.webp')
    t = get_image_mime_type(fpath)
    assert t == "image/webp"
