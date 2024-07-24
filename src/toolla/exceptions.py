class MessageTooLongException(Exception):
    def __init__(self, message="Error: Message is too long"):
        self.message = message
        super().__init__(self.message)

class AbortedToolException(Exception):
    def __init__(self, message="Error: User aborted tool use."):
        self.message = message
        super().__init__(self.message)


class ModelNotSupportedException(Exception):
    def __init__(self, message="Error: Model not supported by library."):
        self.message = message
        super().__init__(self.message)

class ImageNotSupportedException(Exception):
    def __init__(self, message="Error: Image content not supported by API."):
        self.message = message
        super().__init__(self.message)

class InvalidDescriptionException(Exception):
    def __init__(self, message="Error: Invalid description."):
        self.message = message
        super().__init__(self.message)