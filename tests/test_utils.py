import pytest
import base64
from pathlib import Path
from toolla.utils import (
    build_claude_tool_schema,
    build_openai_tool_schema,
    load_file_base64,
    get_image_mime_type,
    parse_response_to_json,
    extract_first_json_block,
    parse_descriptions,
)
from toolla.exceptions import InvalidDescriptionException
from .tools import add, question, multiply

def test_extract_json_block_fail():
    s = 'Now that we have the final result, we can conclude the calculation.\n\nThe final answer is 13544.'
    parsed_s = extract_first_json_block(s)
    assert parsed_s == None

def test_extract_json_block_succed():
    s = 'To calculate this expression, we need to follow the order of operations (PEMDAS):\n\n1. Multiply 1313 and 10\n2. Add 414 to the result\n\nTo do this, we can use the "multiply" tool to multiply 1313 and 10, and then use the "add" tool to add 414 to the result.\n\nHere are the tools and inputs to use:\n\n```json\n{\n  "tool": "multiply",\n  "inputs": {\n    "x": 1313,\n    "y": 10\n  }\n}\n```\n\nPlease use the "multiply" tool with the inputs above, and then add the result to the conversation. I\'ll then guide you on the next step.'
    parsed_s = extract_first_json_block(s)
    assert parsed_s['tool'] == 'multiply'
    assert parsed_s['inputs']['x'] == 1313
    assert parsed_s['inputs']['y'] == 10

def test_parse_description_succeed():
    descriptions = parse_descriptions(add.__doc__)
    assert descriptions['fn_description'] == "An adder function that allows for all types."
    assert descriptions['x'] == "The first number to add."
    assert descriptions['y'] == "The second number to add."
    assert descriptions['z'] == "The third variable."

def test_failed_description_parse():
    with pytest.raises(InvalidDescriptionException) as excinfo:
        description = """
        This is a test description
        """
        descriptions = parse_descriptions(description)
    assert str(excinfo.value) == "Error: Invalid description."

def test_build_openai_tool_schema():
    schema = build_openai_tool_schema(add)
    expected = {
        "type": "function",
        "function": {
            "name": "add",
            "description": "An adder function that allows for all types.",
            "parameters": {
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
    }
    assert schema == expected

def test_build_openai_tool_schema_with_enum():
    schema = build_openai_tool_schema(question)
    expected = {
        "type": "function",
        "function": {
            "name": "question",
            "description": "Answer to a question",
            "parameters": {
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
    }
    assert schema == expected

def test_build_claude_tool_schema():
    schema = build_claude_tool_schema(add)
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

def test_build_claude_schema_with_enum():
    schema = build_claude_tool_schema(question)
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

def test_correctly_parses_to_json():
    response_string = 'I can help you with that. To calculate the sum of 44 and 18811, I recommend using the "add" tool. \n\nHere is the JSON output:\n\n```\n{\n  "tool": "add",\n  "inputs": {\n    "a": 44,\n    "b": 18811\n  }\n}\n```\n\nPlease use the "add" tool with the given inputs and add the result to the conversation. I\'ll be happy to help with the next step.'
    parsed_json = parse_response_to_json(response_string)
    assert parsed_json['tool'] == 'add'
    assert parsed_json['inputs']['a'] == 44
    assert parsed_json['inputs']['b'] == 18811

def test_correctly_parses_to_json_2():
    response_string = 'I can help you with that. To calculate the sum of 44 and 18811, I recommend using the "add" tool. \n\nHere is the JSON output:\n\n```\n{\n  "tool": "multiply",\n  "inputs": {\n    "a": 405,\n    "b": 181\n  }\n}\n```\n\nPlease use the "add" tool with the given inputs and add the result to the conversation. I\'ll be happy to help with the next step.'
    parsed_json = parse_response_to_json(response_string)
    assert parsed_json['tool'] == 'multiply'
    assert parsed_json['inputs']['a'] == 405
    assert parsed_json['inputs']['b'] == 181
