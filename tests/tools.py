from enum import Enum

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

def add(x: int, y: int) -> int:
    """
    An adder function that allows for all types.    

    x: The first number to add.
    y: The second number to add.
    """
    return x + y

def multiply(x: int, y: int) -> int:
    """
    A function for muliplying two integers.

    x: The first integer
    y: The second integer
    """
    return x * y

def concat(first: str, second: str) -> str:
    """
    A function to concatenate strings

    first: The first string
    second: The second string

    returns concatenated string
    """
    return first + second

