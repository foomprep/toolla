# import pytest
# import random
# import string
# import builtins
# from toolla.chat import Chat
# from toolla.exceptions import (
#     MessageTooLongException,
#     AbortedToolException,
#     ImageNotSupportedException,
# )
# from toolla.models import models
# from .tools import add, multiply, concat

# def test_fireworks_llama3_1_405b_instruct_turbo_add_tool():
#     chat = Chat(model="accounts/fireworks/models/llama-v3p1-405b-instruct", tools=[add])
#     r = chat("What is 341+18?")
#     assert r == 359

# def test_fireworks_llama_concat_tool():
#     chat = Chat(model="accounts/fireworks/models/llama-v3p1-405b-instruct", tools=[concat])
#     r = chat("Concatenate the strings dream and tremor")
#     assert r == "dreamtremor"

# # def test_fireworks_image_content():
# #     chat = Chat(model="accounts/fireworks/models/llama-v3p1-405b-instruct")
# #     chat(prompt="What is this an image of? Answer with one word.", image="./tests/cat.jpg")
# #     messages = chat.get_messages()
# #     assert 'Cat' in messages[-1]['content'] or 'cat' in messages[-1]['content']
# def test_fireworks_image_not_supported():
#     with pytest.raises(ImageNotSupportedException) as exc_info:
#         chat = Chat(model="accounts/fireworks/models/llama-v3p1-405b-instruct")
#         chat(prompt="What is this an image of? Answer with one word.", image="./cat.jpg")
#     assert str(exc_info.value) == "Error: Image content not supported by API."

# def test_fireworks_llama_multiple_tools():
#     chat = Chat(model="accounts/fireworks/models/llama-v3p1-405b-instruct", tools=[add, multiply])
#     r = chat("What is (4*4911)+18?")
#     assert r == 19662

# def test_fireworks_large_message_fail():
#     with pytest.raises(MessageTooLongException) as exc_info:
#         characters = string.ascii_letters + string.digits + string.punctuation
#         prompt = ''.join(random.choice(characters) for _ in range(2000000))
#         chat = Chat(model="accounts/fireworks/models/llama-v3p1-405b-instruct")
#         r = chat(prompt=prompt)
#     assert str(exc_info.value) == "Error: Message is too long"

# def test_fireworks_disable_auto_execution_answer_no():
#     with pytest.raises(AbortedToolException) as exc_info:
#         builtins.input = lambda _: 'n'
#         chat = Chat(model="accounts/fireworks/models/llama-v3p1-405b-instruct", tools=[add])
#         chat("What is 44911+18?", disable_auto_execution=True)
#     assert str(exc_info.value) == "Error: User aborted tool use."
