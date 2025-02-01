from .tree_processor import TreeProcessor
from code_sushi.types import File, CodeFragment
from code_sushi.context import Context, LogLevel
from typing import List

class Itamae:
    """
    The Itamae is the module responsible for precisely slicing the code into logical chunks.
    """
    _instance = None
    context: Context

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, context: Context):
        self.context = context

    def slice(self, file: File) -> List[CodeFragment]:
        """
        Process the file to and extract every individual function.
        """
        try:
            if self.context.is_log_level(LogLevel.VERBOSE):
                print(f"Slicing chunks for file: {file.relative_path}")

            parser = TreeProcessor(self.context, file)
            if not parser.is_supported():
                if self.context.is_log_level(LogLevel.VERBOSE):
                    print(f"File {file.relative_path} is not supported by the parser")
                return []

            functions = parser.extract()

            if self.context.is_log_level(LogLevel.VERBOSE) and len(functions) > 0:
                print(f"Functions extracted from {file.relative_path}: {len(functions)}")

            return functions
        except Exception as e:
            print(f"Error in Itamae.slice(): {e}")
            return []
