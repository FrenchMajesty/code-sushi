class LogicalChunk:
    """
    Represents a logical chunk of code. Often a function or method.
    """

    def __init__(self, name: str, code: str, location: str):
        self.name = name
        self.code = code
        self.location = location
