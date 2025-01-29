import os
from tree_sitter import Parser, Tree
from .utils import extract_functions, init_parser, save_raw_function
from .logical_chunk import LogicalChunk
from code_sushi.core import File
from code_sushi.context import Context, LogLevel
from typing import Optional, List

class Itamae:
    """
    The Itamae is the module responsible for precisely slicing the code into logical chunks.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def slice_chunks(self, context: Context, file: File) -> List[LogicalChunk]:
        """Process the file to and extract every individual function."""
        try:
            if context.log_level.value >= LogLevel.VERBOSE.value:
                print(f"Slicing chunks for file: {file.relative_path}")

            parser = init_parser(context, file.ext)
            if not parser:
                return []

            code, syntax_tree = self.parse_content(parser, file.absolute_path)

            functions = extract_functions(code, syntax_tree)
            if context.log_level.value >= LogLevel.VERBOSE.value:
                print(f"Extracted {len(functions)} functions/methods from {file.relative_path}")

            # Parse each function into a logical chunk object
            chunks = []
            for func in functions:
                output_dir = context.output_dir + "/" + file.relative_path + ".functions/"
                output_dir = output_dir.replace("//", "/")
                file_path = save_raw_function(func, output_dir, file.ext)

                if context.log_level.value >= LogLevel.VERBOSE.value:
                    print(f"Saved function: {file_path}")

                chunks.append(LogicalChunk(context, file, func["name"], func["code"], file_path))

            return chunks
        except Exception as e:
            print(f"Error slicing chunks: {e}")
            return []

    def parse_content(self, parser: Parser, file_path: str) -> tuple[str, Tree]:
        """Parse the content of the file and return the syntax tree."""

        try:
            code = open(file_path, "r", encoding="utf8").read()
            tree = parser.parse(bytes(code, "utf8"))
            return code, tree
        except Exception as e:
            print(f"Error parsing content: {e}")
            raise e
