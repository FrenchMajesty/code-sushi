from .code_fragment import CodeFragment
from .tree_processor import TreeProcessor
from code_sushi.core import File
from code_sushi.context import Context, LogLevel
from typing import List

class Itamae:
    """
    The Itamae is the module responsible for precisely slicing the code into logical chunks.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def slice_chunks(self, context: Context, file: File) -> List[CodeFragment]:
        """Process the file to and extract every individual function."""
        try:
            if context.is_log_level(LogLevel.VERBOSE):
                print(f"Slicing chunks for file: {file.relative_path}")

            parser = TreeProcessor(context, file)
            if not parser.is_supported():
                return []

            functions = parser.extract()

            if context.is_log_level(LogLevel.VERBOSE):
                print(f"Extracted {len(functions)} functions/methods from {file.relative_path}")

            return functions
        except Exception as e:
            print(f"Error slicing chunks: {e}")
            return []
