from code_sushi.core import File

class LogicalChunk:
    """
    Represents a logical chunk of code. Often a function or method.
    """

    def __init__(self, parent: File, name: str, code: str, location: str):
        self.parent = parent
        self.name = name
        self.code = code
        self.location = location
